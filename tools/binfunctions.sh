#!/bin/bash
b=$1; d=$2; mkdir -p "$d"; rm -f "$d"/*
objdump -d --no-show-raw-insn "$b" | awk -v d="$d" '
 /^[0-9a-f]+ <.*>:$/ { name=substr($0, index($0,"<")+1); sub(/>:$/,"",name); f=d "/" name; next }
 /^$/ { next }
 { line=$0; sub(/^ *[0-9a-f]+:\t/,"",line);
   gsub(/0x[0-9a-f]+/,"#",line); gsub(/[0-9a-f]+ </,"# <",line);
   if (f!="") print line >> f }
'
