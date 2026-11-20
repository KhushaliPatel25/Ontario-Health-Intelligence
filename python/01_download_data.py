
from pathlib import Path
from urllib.request import Request, urlopen

# Find the project folder automatically
project_dir = Path(__file__).resolve().parent.parent

# Where the original dataset will be saved
raw_dir = project_dir / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

# Official CIHI dataset URL
url = (
    "https://www.cihi.ca/sites/default/files/document/"
    "data-file/810-total-time-spent-in-emergency-department-"
    "for-admitted-patients-data-table-en.xlsx"
)

output_file = raw_dir / "cihi_ed_wait_times.xlsx"

print("Downloading official CIHI healthcare data...")

try:
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(request, timeout=60) as response:
        data = response.read()

    if not data.startswith(b"PK"):
        raise ValueError("Downloaded content is not an XLSX workbook.")

    output_file.write_bytes(data)

    print("Download successful!")
    print(f"Saved to: {output_file}")
    print(f"File size: {len(data):,} bytes")

except Exception as error:
    raise RuntimeError(f"CIHI download failed: {error}") from error
