# LSR Download Monitor

This repository automatically monitors the [LSR (LilyPond Snippet Repository) download page](https://lsr.di.unimi.it/download/) and downloads any new or updated files daily.

## What it monitors

The system tracks the following types of files from the LSR download page:
- **Database dumps** (`lsr-*.mysqldump.gz`) - Full database snapshots
- **Snippet collections** (`lsr-snippets-*.tar.gz`) - All snippets as individual files
- **Documentation** (`lsr-snippets-docs-*.tar.gz`) - Documentation for snippets
- **Source code** (`lsr-*-src.tar.gz`) - GPL source code of LSR

## How it works

1. **Daily monitoring**: GitHub Actions runs the monitor script every day at 6 AM UTC
2. **Change detection**: Compares file sizes and modification dates to detect changes
3. **Smart downloading**: Only downloads files that are new or have changed
4. **Automatic commits**: Commits any new or updated files to the repository
5. **Metadata tracking**: Maintains a `downloads/metadata.json` file with download history

## File structure

```
.
├── .github/workflows/lsr-monitor.yml  # GitHub Actions workflow
├── scripts/lsr_monitor.py             # Python monitoring script
├── downloads/                         # Downloaded files directory
│   ├── metadata.json                  # Tracking metadata
│   ├── lsr-YYYY-MM-DD.mysqldump.gz   # Database dumps
│   ├── lsr-snippets-all-*.tar.gz     # Snippet collections
│   └── ...                           # Other LSR files
└── README.md                          # This file
```

## Setup Instructions

1. **Create a new GitHub repository** for this project

2. **Add the files** to your repository:
   - Copy the `.github/workflows/lsr-monitor.yml` file
   - Copy the `scripts/lsr_monitor.py` file
   - Copy this `README.md` file

3. **Enable GitHub Actions** (usually enabled by default)

4. **Manual trigger** (optional): You can manually trigger the workflow from the Actions tab

## Customization

### Change the schedule
Edit the cron expression in `.github/workflows/lsr-monitor.yml`:
```yaml
schedule:
  - cron: '0 6 * * *'  # Daily at 6 AM UTC
```

Common schedules:
- `'0 */6 * * *'` - Every 6 hours
- `'0 12 * * *'` - Daily at noon UTC
- `'0 6 * * 1'` - Weekly on Mondays at 6 AM UTC

### Filter specific files
Modify the `parse_file_list()` function in `scripts/lsr_monitor.py` to filter files by name patterns.

### Change download location
Update the `DOWNLOADS_DIR` variable in `scripts/lsr_monitor.py`.

## Monitoring and logs

- Check the **Actions** tab in your GitHub repository to see workflow runs
- Each run shows detailed logs of what files were checked and downloaded
- Failed runs will show error messages for troubleshooting
   
