
## Description
A module for scanning WordPress pages using the [WPScan](https://wpscan.com/) tool.

## Prerequisites
[WPScan](https://www.kali.org/tools/wpscan/) must be installed.

## Input parameters

=== "Simple"

    ### `target`
    Scan target.
    
    | Name     | Type   | Required | Default value | Example value            |
    |----------|--------|----------|---------------|--------------------------|
    | `target` | string | &check;  |               | `http://127.0.0.1:8000/` |
    
    ### `api_token`
    The WPScan API Token to display vulnerability data, available at https://wpscan.com/profile.
    
    | Name        | Type   | Required | Default value | Example value |
    |-------------|--------|----------|---------------|---------------|
    | `api_token` | string | &cross;  |               |               |
    
    ### `options`
    Additional WPScan parameters.
    
    | Name      | Type   | Required | Default value | Example value     |
    |-----------|--------|----------|---------------|-------------------|
    | `options` | string | &cross;  |               | `--max-threads 7` |
    
    ### `serialize_output`
    Use WPScan's serialization (`-f json`).
    
    | Name               | Type    | Required | Default value | Example value |
    |--------------------|---------|----------|---------------|---------------|
    | `serialize_output` | boolean | &cross;  | `true`        | `false`       |

=== "Custom"

    ### `command`
    WPScan command to run with syntax as in command line (with executable).
    
    | Name      | Type   | Required | Default value | Example value                                 |
    |-----------|--------|----------|---------------|-----------------------------------------------|
    | `command` | string | &check;  |               | `wpscan --url http://127.0.0.1:8000/ -f json` |
    
    For the scan result to be in the `serialized_output`, use `-f json` parameter.

## Examples

### Example with serialized output
Input:
```yaml
my-step:
  module: wpscan
  arguments:
    target: {{ target }}
    options: --max-threads 7

```

Output:
```json
{
  "result": "ok", 
  "output": "", 
  "serialized_output": {"banner": {"description": "WordPress Security Scanner by the WPScan Team", "version": "3.8.22", "authors": ["@_WPScan_", "@ethicalhack3r", "@erwan_lr", "@firefart"], "sponsor": "Sponsored by Automattic - https://automattic.com/"}, "start_time": 1667510731, "start_memory": 50909184, "target_url": "http://127.12.0.1/", "target_ip": "127.12.0.1", "effective_url": "http://127.12.0.1/", "interesting_findings": [{"url": "http://127.12.0.1/", "to_s": "Headers", "type": "headers", "found_by": "Headers (Passive Detection)", "confidence": 100, "confirmed_by": {}, "references": {}, "interesting_entries": ["Server: Apache/2.4.7 (Ubuntu)", "X-Powered-By: PHP/5.5.9-1ubuntu4.29", "SecretHeader: SecretValue", "via: Squid 1.0.0"]}, {"url": "http://127.12.0.1/robots.txt", "to_s": "robots.txt found: http://127.12.0.1/robots.txt", "type": "robots_txt", "found_by": "Robots Txt (Aggressive Detection)", "confidence": 100, "confirmed_by": {}, "references": {}, "interesting_entries": []}, {"url": "http://127.12.0.1/searchreplacedb2.php", "to_s": "Search Replace DB script found: http://127.12.0.1/searchreplacedb2.php", "type": "search_replace_db2", "found_by": "Search Replace Db2 (Aggressive Detection)", "confidence": 100, "confirmed_by": {}, "references": {"url": ["https://interconnectit.com/products/search-and-replace-for-wordpress-databases/"]}, "interesting_entries": []}, {"url": "http://127.12.0.1/xmlrpc.php", "to_s": "XML-RPC seems to be enabled: http://127.12.0.1/xmlrpc.php", "type": "xmlrpc", "found_by": "Headers (Passive Detection)", "confidence": 100, "confirmed_by": {"Link Tag (Passive Detection)": {"confidence": 30}, "Direct Access (Aggressive Detection)": {"confidence": 100}}, "references": {"url": ["http://codex.wordpress.org/XML-RPC_Pingback_API"], "metasploit": ["auxiliary/scanner/http/wordpress_ghost_scanner", "auxiliary/dos/http/wordpress_xmlrpc_dos", "auxiliary/scanner/http/wordpress_xmlrpc_login", "auxiliary/scanner/http/wordpress_pingback_access"]}, "interesting_entries": []}, {"url": "http://127.12.0.1/readme.html", "to_s": "WordPress readme found: http://127.12.0.1/readme.html", "type": "readme", "found_by": "Direct Access (Aggressive Detection)", "confidence": 100, "confirmed_by": {}, "references": {}, "interesting_entries": []}, {"url": "http://127.12.0.1/wp-content/debug.log", "to_s": "Debug Log found: http://127.12.0.1/wp-content/debug.log", "type": "debug_log", "found_by": "Direct Access (Aggressive Detection)", "confidence": 100, "confirmed_by": {}, "references": {"url": ["https://codex.wordpress.org/Debugging_in_WordPress"]}, "interesting_entries": []}, {"url": "http://127.12.0.1/wp-cron.php", "to_s": "The external WP-Cron seems to be enabled: http://127.12.0.1/wp-cron.php", "type": "wp_cron", "found_by": "Direct Access (Aggressive Detection)", "confidence": 60, "confirmed_by": {}, "references": {"url": ["https://www.iplocation.net/defend-wordpress-from-ddos", "https://github.com/wpscanteam/wpscan/issues/1299"]}, "interesting_entries": []}], "version": {"number": "4.2.34", "release_date": "0001-01-01", "status": "outdated", "found_by": "Rss Generator (Passive Detection)", "confidence": 100, "interesting_entries": ["http://127.12.0.1/index.php/feed/, <generator>https://wordpress.org/?v=4.2.34</generator>", "http://127.12.0.1/index.php/comments/feed/, <generator>https://wordpress.org/?v=4.2.34</generator>"], "confirmed_by": {}, "vulnerabilities": []}, "main_theme": {"slug": "twentyfifteen", "location": "http://127.12.0.1/wp-content/themes/twentyfifteen/", "latest_version": "3.3", "last_updated": "2022-11-02T00:00:00.000Z", "outdated": true, "readme_url": "http://127.12.0.1/wp-content/themes/twentyfifteen/readme.txt", "directory_listing": true, "error_log_url": null, "style_url": "http://127.12.0.1/wp-content/themes/twentyfifteen/style.css?ver=4.2.34", "style_name": "Twenty Fifteen", "style_uri": "https://wordpress.org/themes/twentyfifteen/", "description": "Our 2015 default theme is clean, blog-focused, and designed for clarity. Twenty Fifteen's simple, straightforward typography is readable on a wide variety of screen sizes, and suitable for multiple languages. We designed it using a mobile-first approach, meaning your content takes center-stage, regardless of whether your visitors arrive by smartphone, tablet, laptop, or desktop computer.", "author": "the WordPress team", "author_uri": "https://wordpress.org/", "template": null, "license": "GNU General Public License v2 or later", "license_uri": "http://www.gnu.org/licenses/gpl-2.0.html", "tags": "black, blue, gray, pink, purple, white, yellow, dark, light, two-columns, left-sidebar, fixed-layout, responsive-layout, accessibility-ready, custom-background, custom-colors, custom-header, custom-menu, editor-style, featured-images, microformats, post-formats, rtl-language-support, sticky-post, threaded-comments, translation-ready", "text_domain": "twentyfifteen", "found_by": "Css Style In Homepage (Passive Detection)", "confidence": 70, "interesting_entries": [], "confirmed_by": {}, "vulnerabilities": [], "version": {"number": "1.1", "confidence": 80, "found_by": "Style (Passive Detection)", "interesting_entries": ["http://127.12.0.1/wp-content/themes/twentyfifteen/style.css?ver=4.2.34, Match: 'Version: 1.1'"], "confirmed_by": {}}, "parents": []}, "plugins": {}, "config_backups": {"http://127.12.0.1/wp-config.old": {"found_by": "Direct Access (Aggressive Detection)", "confidence": 100, "interesting_entries": [], "confirmed_by": {}}, "http://127.12.0.1/wp-config.php.save": {"found_by": "Direct Access (Aggressive Detection)", "confidence": 100, "interesting_entries": [], "confirmed_by": {}}, "http://127.12.0.1/wp-config.php~": {"found_by": "Direct Access (Aggressive Detection)", "confidence": 100, "interesting_entries": [], "confirmed_by": {}}, "http://127.12.0.1/wp-config.txt": {"found_by": "Direct Access (Aggressive Detection)", "confidence": 100, "interesting_entries": [], "confirmed_by": {}}}, "vuln_api": {"error": "No WPScan API Token given, as a result vulnerability data has not been output.\nYou can get a free API token with 25 daily requests by registering at https://wpscan.com/register"}, "stop_time": 1667510735, "elapsed": 4, "requests_done": 139, "cached_requests": 44, "data_sent": 34812, "data_sent_humanised": "33.996 KB", "data_received": 20794, "data_received_humanised": "20.307 KB", "used_memory": 244031488, "used_memory_humanised": "232.727 MB"}
}
```

### Example with text output
Input:
```yaml
my-step:
  module: wpscan
  arguments:
    target: {{ target }}
    options: --max-threads 7
    serialized_output: false

```

Output:
```json
{
  "result": "ok", 
  "output": "_______________________________________________________________\n         __          _______   _____\n         \\ \\        / /  __ \\ / ____|\n          \\ \\  /\\  / /| |__) | (___   ___  __ _ _ __ ®\n           \\ \\/  \\/ / |  ___/ \\___ \\ / __|/ _` | '_ \\\n            \\  /\\  /  | |     ____) | (__| (_| | | | |\n             \\/  \\/   |_|    |_____/ \\___|\\__,_|_| |_|\n\n         WordPress Security Scanner by the WPScan Team\n                         Version 3.8.17\n       Sponsored by Automattic - https://automattic.com/\n       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart\n_______________________________________________________________\n\n\x1b[32m[+]\x1b[0m URL: http://127.12.0.1/ [127.12.0.1]\n\x1b[32m[+]\x1b[0m Started: Mon Nov  7 15:56:24 2022\n\nInteresting Finding(s):\n\n\x1b[32m[+]\x1b[0m Headers\n | Interesting Entries:\n |  - Server: Apache/2.4.7 (Ubuntu)\n |  - X-Powered-By: PHP/5.5.9-1ubuntu4.29\n |  - SecretHeader: SecretValue\n |  - via: Squid 1.0.0\n | Found By: Headers (Passive Detection)\n | Confidence: 100%\n\n\x1b[32m[+]\x1b[0m robots.txt found: http://127.12.0.1/robots.txt\n | Found By: Robots Txt (Aggressive Detection)\n | Confidence: 100%\n\n\x1b[32m[+]\x1b[0m Search Replace DB script found: http://127.12.0.1/searchreplacedb2.php\n | Found By: Search Replace Db2 (Aggressive Detection)\n | Confidence: 100%\n | Reference: https://interconnectit.com/products/search-and-replace-for-wordpress-databases/\n\n\x1b[32m[+]\x1b[0m XML-RPC seems to be enabled: http://127.12.0.1/xmlrpc.php\n | Found By: Headers (Passive Detection)\n | Confidence: 100%\n | Confirmed By:\n |  - Link Tag (Passive Detection), 30% confidence\n |  - Direct Access (Aggressive Detection), 100% confidence\n | References:\n |  - http://codex.wordpress.org/XML-RPC_Pingback_API\n |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/\n |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/\n |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/\n |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/\n\n\x1b[32m[+]\x1b[0m WordPress readme found: http://127.12.0.1/readme.html\n | Found By: Direct Access (Aggressive Detection)\n | Confidence: 100%\n\n\x1b[32m[+]\x1b[0m Debug Log found: http://127.12.0.1/wp-content/debug.log\n | Found By: Direct Access (Aggressive Detection)\n | Confidence: 100%\n | Reference: https://codex.wordpress.org/Debugging_in_WordPress\n\n\x1b[32m[+]\x1b[0m The external WP-Cron seems to be enabled: http://127.12.0.1/wp-cron.php\n | Found By: Direct Access (Aggressive Detection)\n | Confidence: 60%\n | References:\n |  - https://www.iplocation.net/defend-wordpress-from-ddos\n |  - https://github.com/wpscanteam/wpscan/issues/1299\n\n\x1b[32m[+]\x1b[0m WordPress version 4.2.34 identified (Outdated, released on 0001-01-01).\n | Found By: Rss Generator (Passive Detection)\n |  - http://127.12.0.1/index.php/feed/, <generator>https://wordpress.org/?v=4.2.34</generator>\n |  - http://127.12.0.1/index.php/comments/feed/, <generator>https://wordpress.org/?v=4.2.34</generator>\n\n\x1b[32m[+]\x1b[0m WordPress theme in use: twentyfifteen\n | Location: http://127.12.0.1/wp-content/themes/twentyfifteen/\n | Last Updated: 2022-11-02T00:00:00.000Z\n | Readme: http://127.12.0.1/wp-content/themes/twentyfifteen/readme.txt\n | \x1b[33m[!]\x1b[0m The version is out of date, the latest version is 3.3\n | Style URL: http://127.12.0.1/wp-content/themes/twentyfifteen/style.css?ver=4.2.34\n | Style Name: Twenty Fifteen\n | Style URI: https://wordpress.org/themes/twentyfifteen/\n | Description: Our 2015 default theme is clean, blog-focused, and designed for clarity. Twenty Fifteen's simple, st...\n | Author: the WordPress team\n | Author URI: https://wordpress.org/\n |\n | Found By: Css Style In Homepage (Passive Detection)\n |\n | Version: 1.1 (80% confidence)\n | Found By: Style (Passive Detection)\n |  - http://127.12.0.1/wp-content/themes/twentyfifteen/style.css?ver=4.2.34, Match: 'Version: 1.1'\n\n\x1b[32m[+]\x1b[0m Enumerating All Plugins (via Passive Methods)\n\n\x1b[34m[i]\x1b[0m No plugins Found.\n\n\x1b[32m[+]\x1b[0m Enumerating Config Backups (via Passive and Aggressive Methods)\n\n Checking Config Backups -: |==================================================|\n\n\x1b[34m[i]\x1b[0m Config Backup(s) Identified:\n\n\x1b[31m[!]\x1b[0m http://127.12.0.1/wp-config.old\n | Found By: Direct Access (Aggressive Detection)\n\n\x1b[31m[!]\x1b[0m http://127.12.0.1/wp-config.php.save\n | Found By: Direct Access (Aggressive Detection)\n\n\x1b[31m[!]\x1b[0m http://127.12.0.1/wp-config.php~\n | Found By: Direct Access (Aggressive Detection)\n\n\x1b[31m[!]\x1b[0m http://127.12.0.1/wp-config.txt\n | Found By: Direct Access (Aggressive Detection)\n\n\x1b[33m[!]\x1b[0m No WPScan API Token given, as a result vulnerability data has not been output.\n\x1b[33m[!]\x1b[0m You can get a free API token with 25 daily requests by registering at https://wpscan.com/register\n\n\x1b[32m[+]\x1b[0m Finished: Mon Nov  7 15:56:34 2022\n\x1b[32m[+]\x1b[0m Requests Done: 139\n\x1b[32m[+]\x1b[0m Cached Requests: 44\n\x1b[32m[+]\x1b[0m Data Sent: 34.132 KB\n\x1b[32m[+]\x1b[0m Data Received: 20.307 KB\n\x1b[32m[+]\x1b[0m Memory used: 243.156 MB\n\x1b[32m[+]\x1b[0m Elapsed time: 00:00:10\n", 
  "serialized_output": {}
}
```

## Troubleshooting
So far so good.

## Output serialization
Output is serialized by WPScan itself.
