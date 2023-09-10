# To-Do List for CLI MyLead API Tool

## Introduction

This document outlines the steps to create a CLI MyLead API Tool, which includes fetching data from an API, storing it in a Pandas DataFrame, providing a CLI interface using Typer, and visualizing the data using Seaborn.

---

## 1. Async Request to API using httpx and asyncio

### Tasks

- [x] Import `httpx` and `asyncio`
- [x] Write an asynchronous function to fetch data from the API
- [x] Include error handling
- [x] Paginate through API results
- [x] Assemble all data into a single structure

---

## 2. Storing Data in DataFrame

### Tasks

- [x] Import Pandas
- [x] Validate and modfiy data via Pydantic
- [x] Convert the API JSON response to a Pandas DataFrame
  - [x] Utilize `pd.json_normalize()` if needed
- [x] Handle nested data and create new columns if necessary
- [x] Inspect the DataFrame to ensure data is correctly loaded

---

## 3. Make CLI Support with Typer

### Tasks

- [x] Install and import Typer
- [x] Create main CLI function
- [ ] Add sub-commands for different operations
  - [ ] `API KEY support`
    - [ ] Add an option to specify API KEY
  - [ ] `Saving data to file`
    - [ ] Implement a `save` command to export DataFrame to CSV/Excel
  - [ ] `Statistics`
    - [ ] Implement a `stats` command to show summary statistics
  - [ ] `Max/min, avg lead`
    - [ ] Implement a `lead-stats` command to show max, min, and average lead

---

## 4. Graphs with Seaborn

### Tasks

- [ ] Install and import Seaborn
- [ ] Create visualizations based on DataFrame
  - [ ] Line graphs for time-based data
  - [ ] Bar graphs for categorical data
  - [ ] Heatmaps for correlations

---

## Final Steps

- [ ] Test all functionalities
- [ ] Document the code properly
- [ ] Optimize for performance
