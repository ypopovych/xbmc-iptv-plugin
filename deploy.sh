#!/bin/sh

REPO_DIR="xbmc_repo"

script_name=`basename $0`
script_path=`dirname $0`

cd $script_path

for f in ./plugin.*
do
	echo "Plugin found: $f"
	version=`cat $f/addon.xml | sed -En 's/.*version="([[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+)"/\\1/p' | tr -d '\015\032'`
	addon_name=`basename $f`
	if [ ! -d "$REPO_DIR/$addon_name" ]; then
		mkdir "$REPO_DIR/$addon_name"
	fi
	rm -f "$REPO_DIR/$addon_name/$addon_name-$version.zip"
	zip -r "$REPO_DIR/$addon_name/$addon_name-$version.zip" "$addon_name"
	cp -f "$f/icon.png" "$REPO_DIR/$addon_name" 
	cp -f "$f/changelog.txt" "$REPO_DIR/$addon_name"
	cp -f "$f/changelog.txt" "$REPO_DIR/$addon_name/changelog-$version.txt"
	cp -f "$f/fanart.jpg" "$REPO_DIR/$addon_name"
done

python addons_xml_generator.py
