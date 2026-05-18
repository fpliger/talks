"""File System Access API bridge for Demo 3's save_to_file tool.

On the first save in a session, prompts the user:
  "Download the file" or "Mount a local folder"

Mounted-folder mode uses window.showDirectoryPicker() and writes
through the returned FileSystemDirectoryHandle — the file lands
on the user's actual disk with no backend involved.

Falls back to download mode when the API is unavailable (Safari/Firefox).
"""

from pyscript import window, document
from pyodide.ffi import create_proxy
import asyncio


_dir_handle = None       # cached FileSystemDirectoryHandle
_save_mode = None        # "download" | "folder" | None (not yet chosen)


def _fs_access_supported() -> bool:
    return hasattr(window, "showDirectoryPicker")


async def _ask_save_mode() -> str:
    """Show a modal and return 'download' or 'folder'."""
    if not _fs_access_supported():
        return "download"

    # Build modal
    modal = document.createElement("div")
    modal.id = "fs-modal"
    modal.innerHTML = """
    <div style="
        position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:9999;
        display:flex;align-items:center;justify-content:center;">
      <div style="
          background:#1a1d23;border:1px solid #333;border-radius:12px;
          padding:2rem;max-width:420px;width:90%;color:#e0e0e0;font-family:system-ui;">
        <h3 style="margin:0 0 .75rem;font-size:1.1rem;">Where should the agent save the file?</h3>
        <p style="margin:0 0 1.5rem;font-size:.9rem;color:#aaa;line-height:1.5;">
          The agent wants to write <strong>climate_notes.md</strong> to disk.
          Choose how you'd like this to work.
        </p>
        <div style="display:flex;gap:.75rem;flex-direction:column;">
          <button id="fs-folder" style="
              padding:.75rem 1rem;border-radius:8px;border:2px solid #20c997;
              background:transparent;color:#20c997;cursor:pointer;font-size:.95rem;text-align:left;">
            📁  Mount a local folder — agent writes directly to your disk
          </button>
          <button id="fs-download" style="
              padding:.75rem 1rem;border-radius:8px;border:2px solid #555;
              background:transparent;color:#aaa;cursor:pointer;font-size:.95rem;text-align:left;">
            ⬇️  Download — browser saves the file to Downloads
          </button>
        </div>
      </div>
    </div>"""
    document.body.appendChild(modal)

    chosen = await _wait_for_choice()
    document.body.removeChild(modal)
    return chosen


async def _wait_for_choice() -> str:
    result = [None]

    def on_folder(e):
        result[0] = "folder"

    def on_download(e):
        result[0] = "download"

    folder_proxy = create_proxy(on_folder)
    download_proxy = create_proxy(on_download)

    document.getElementById("fs-folder").addEventListener("click", folder_proxy)
    document.getElementById("fs-download").addEventListener("click", download_proxy)

    while result[0] is None:
        await asyncio.sleep(0.05)

    folder_proxy.destroy()
    download_proxy.destroy()
    return result[0]


async def save_file(filename: str, content: str) -> str:
    """Save content to a file.

    Returns a human-readable status string for the agent loop to pass
    back to the LLM as the tool result.
    """
    global _dir_handle, _save_mode

    if _save_mode is None:
        _save_mode = await _ask_save_mode()

    if _save_mode == "folder":
        if _dir_handle is None:
            try:
                _dir_handle = await window.showDirectoryPicker()
            except Exception:
                # User cancelled picker → fall back to download
                _save_mode = "download"

    if _save_mode == "folder" and _dir_handle is not None:
        try:
            file_handle = await _dir_handle.getFileHandle(filename, {"create": True})
            writable = await file_handle.createWritable()
            await writable.write(content)
            await writable.close()
            return f"Saved '{filename}' to your local folder."
        except Exception as e:
            return f"Folder write failed ({e}); try downloading instead."

    # Download mode
    _trigger_download(filename, content)
    return f"Downloaded '{filename}' to your Downloads folder."


def _trigger_download(filename: str, content: str):
    blob = window.Blob.new([content], {"type": "text/markdown"})
    url = window.URL.createObjectURL(blob)
    a = document.createElement("a")
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
