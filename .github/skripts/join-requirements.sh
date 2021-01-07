for entry in ./amos/*; do
  requirements="";
  touch all.txt
  if [ -f $entry/requirements.txt ]; then
    echo ls $entry
    cat $entry/requirements.txt >> ./.github/skripts/all.txt;
  fi
done
