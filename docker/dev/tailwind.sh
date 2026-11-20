#!/bin/sh
set -eu

npm ci
exec npm run dev
