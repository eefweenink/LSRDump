# LSR Download Monitor

This repository automatically monitors the [LSR (LilyPond Snippet Repository) download page](https://lsr.di.unimi.it/download/) and downloads any new or updated files daily.

## What it monitors

The system tracks the following types of files from the LSR download page:
- **Database dumps** (`lsr-*.mysqldump.gz`) - Full database snapshots
- **Snippet collections** (`lsr-snippets-*.tar.gz`) - All snippets as individual files
- **Documentation** (`lsr-snippets-docs-*.tar.gz`) - Documentation for snippets
- **Source code** (`lsr-*-src.tar.gz`) - GPL source code of LSR

## How it works

1. **Frequent monitoring**: GitHub Actions runs the monitor script every 6 hours
2. **Change detection**: Compares file sizes, modification dates, and MD5 hashes to detect changes
3. **Smart downloading**: Only downloads files that are new or have changed
4. **SSL handling**: Gracefully handles SSL certificate issues (currently bypassed due to expired cert)
5. **Automatic commits**: Commits any new or updated files to the repository
6. **Artifact storage**: Files are also stored as GitHub Actions artifacts
7. **Metadata tracking**: Maintains a `downloads/metadata.json` file with download history

## File structure

```
.
├── .github/workflows/lsr-monitor.yml  # GitHub Actions workflow
├── lsr_monitor.py                     # Python monitoring script
├── requirements.txt                   # Python dependencies
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
   - Copy the `lsr_monitor.py` file
   - Copy the `requirements.txt` file
   - Copy this `README.md` file

3. **Enable GitHub Actions** (usually enabled by default)

4. **Manual trigger** (optional): You can manually trigger the workflow from the Actions tab

## Customization

### Change the schedule
Edit the cron expression in `.github/workflows/lsr-monitor.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours (current setting)
```

Common schedules:
- `'0 6 * * *'` - Daily at 6 AM UTC
- `'0 12 * * *'` - Daily at noon UTC
- `'0 6 * * 1'` - Weekly on Mondays at 6 AM UTC

### SSL Certificate Handling
The target website currently has SSL certificate issues. You can control SSL verification:

```python
VERIFY_SSL = os.getenv('VERIFY_SSL', 'false').lower() == 'true'
```

Or set the environment variable in the GitHub Actions workflow:
```yaml
env:
  VERIFY_SSL: 'false'  # Disable SSL verification
```

### Filter specific files
Modify the `parse_file_list()` function in `lsr_monitor.py` to filter files by name patterns.

### Change download location
Update the `DOWNLOADS_DIR` variable in `lsr_monitor.py`.

## Monitoring and logs

- Check the **Actions** tab in your GitHub repository to see workflow runs
- Each run shows detailed logs of what files were checked and downloaded
- Failed runs will show error messages for troubleshooting

## Local testing

You can test the script locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the monitor script
python lsr_monitor.py

# Or with SSL verification enabled
VERIFY_SSL=true python lsr_monitor.py
```

## Storage considerations

The LSR files can be quite large:
- Database dumps: ~7MB each
- Snippet collections: ~2-3MB each
- These accumulate over time as new versions are released

Consider the GitHub repository size limits and clean up old files periodically if needed.

## Troubleshooting

**Workflow not running?**
- Check that Actions are enabled in repository settings
- Verify the YAML syntax in the workflow file

**Downloads failing?**
- Check if the LSR website is accessible
- Review error logs in the Actions tab
- The script includes retry logic for temporary network issues

**Files not being detected as changed?**
- The script relies on modification dates and file sizes
- If the LSR site doesn't update these properly, files might be missed
- Consider adding hash-based comparison for more reliable detection

## Contributing

Feel free to improve the monitoring script or add features like:
- Email notifications on changes
- Slack/Discord webhooks
- File format validation
- Automatic extraction and indexing of snippet content
