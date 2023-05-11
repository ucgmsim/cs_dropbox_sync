# Cybershake Simulation Data - Frontend

## Contents
- [Overview](#overview)
- [Naming](#naming)
- [Requirements](#requirements)
- [Running locally](#running-locally)

## Overview

Frontend Web app to download cybershake simulation data from dropbox.

This is a React/Javascript SPA,  talking to a Python Flask API, running on a Linux host.


## Naming

- **Filename** : PascalCase except index files (ex: index.js, index.html, index.css...)
- **Variables & Functions** : camelCase (ex: requestOptions, formData)
- **HTML Class/ID Names** : All lower case and separate with a hyphen (ex:hi-my-name-is-joel)

## Requirements

- Node v12
- `.env` with the following environment variable.
  - REACT_APP_CS_API_URL=

#### To run Frontend: `npm start`

## Running locally

Open a terminal to do the following steps

1. Change the directory to frontend

```shell
cd /your_path/cs_dropbox_sync/frontend
```

2. Install packages

```shell
npm install
```

3. Start an app

```shell
npm start
```