#!/bin/sh

script_name=`basename $0`
script_path=`dirname $0`

IGNORED_FILES="$script_name README.md"
ADDON_NAME="plugin.video.iptv.viewer"

FTP_HOST="g.if.ua"
FTP_DIR="xbmc"

version=`cat ./addon.xml | sed -En 's/.*version="([[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+)"/\\1/p' | tr -d '\015\032'`
echo "$version"
out_dir="$TMPDIR/$ADDON_NAME"
mkdir "$out_dir"
mkdir "$out_dir/$ADDON_NAME"

for f in $script_path/*
do
	ignored=0
	for fl in $IGNORED_FILES
		do
			if [ "$fl" == "$f" -o "$script_path/$fl" == "$f" ]; then
				ignored=1
				break
			fi
		done
	if [ $ignored == 0 ]; then
		echo "File: $f"
		cp -R "$f" "$out_dir/$ADDON_NAME"
	fi
done
cp "$script_path/addon.xml" "$out_dir"
cd "$out_dir"

md5 -q addon.xml > addon.xml.md5
zip -r "$ADDON_NAME-$version.zip" "$ADDON_NAME"

ftp -n -v $FTP_HOST << EOT
binary
user $1 $2
cd $FTP_DIR
put addon.xml
put addon.xml.md5
cd addons
put "$ADDON_NAME-$version.zip"
bye
EOT

rm -rf "$out_dir"
 