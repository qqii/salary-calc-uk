#!/usr/bin/env bash

set -uo pipefail
# shellcheck disable=SC2154
trap 's=$?; echo "$0: Error on line "$LINENO": $BASH_COMMAND"; exit $s' ERR
IFS=$'\n\t'

# Validate the commit message follows Conventional Commits.
# https://www.conventionalcommits.org/

read -r line < "$1"
[[ $line =~ ^(feat|fix|refactor|perf|style|test|docs|build|ops|chore)(\(.+\))?!?:\ .+ ]] \
  || [[ $line =~ ^(fixup|squash|amend|wip)\! ]]
