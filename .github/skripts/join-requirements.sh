for entry in ./amos/*; do
  touch requirements.txt
  if [ -f $entry/requirements.txt ]; then
    echo ls $entry
    cat $entry/requirements.txt >> ./.github/skripts/requirements.txt;
  fi
done
