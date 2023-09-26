# myleadcli - CLI tool for MyLead API

This package provides a command-line tool for generating statistics and charts from the MyLead API. With it, you can easily retrieve data from the API, store it in a Pandas DataFrame, save it to a file, create a user-friendly CLI interface using Typer, and visualize the data using Plotly.

The data presented by this tool is not available in the standard MyLead dashboard.

It's built on an asynchronous foundation, utilizing the httpx library with HTTP/2 support, and further enhancing performance with orjson. Data integrity is ensured through validation with Pydantic.

**No data is send to third parties.**

## Performance

**Due to API rate limiting, the maximum fetching speed from the API is restricted to 10,000 leads per 60 seconds**

### Examples

Fetching and processing up to 10,000 leads takes approximately 1.5 seconds.

Fetching and processing one million leads from file takes only 40sec.
Fetching same amount from API would rougly take 1h 40min.

The API rate limit acts as a bottleneck. Fortunately, in a typical scenario where a user has around 10,000 to 30,000 leads from the last 365 days, the process usually takes from 2 to 186 seconds.

## Installation

Install with pip

```bash
  pip install myleadcli
```

## Environment Variables

You can provide your API_KEY as environment variables to your .env file or just paste it as argument in command line.

You can get your API_KEY here: https://mylead.global/panel/api

```
API_KEY=YOUR_API_KEY_FROM_MYLEAD_DASHBOARD
```

## Usage/Examples

To fetch and present data in tables for leads from last 365 days use:

```bash
myleadcli YOUR_API_KEY
```

For charts

```bash
myleadcli YOUR_API_KEY --charts
```

For more information use:

```bash
myleadcli --help
```

## Features

- [x] Charts for data not available in MyLead dashboard
- [x] Presenting data in tables
- [x] Async support for best performance
- [x] Utilize categorical data types in Pandas to achieve improved memory usage (resulting in a 45% reduction with real data)
- [ ] Mean/Max/Min/Avg statistics
- [ ] More flexibility with file saving/reading
