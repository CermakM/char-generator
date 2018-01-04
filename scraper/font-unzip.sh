#!/bin/bash

## Unzip all zip files found in the given path


TARGET=$1

[ -z $TARGET ] && printf '%s\n%s\n' 'argument TARGET has not been provided' \
   'TARGET is a path to the parent font directory containing subdirectories with *.zip files' &&  exit 1

find $TARGET -name '*.zip' -type f | xargs -I{} sh -c '\
	font_file={}
	font_dir=${font_file%/*}
	pushd $font_dir >/dev/null
	unzip ${font_file##*/}
	popd >/dev/null'

detox -r 'fonts'  # clean up file names
