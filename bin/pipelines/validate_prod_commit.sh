
if [[ "$2" =~ ProdRelease\/R([0-9]{2})_([0-9]{4})_P$ ]]; then
  test_release_branch="TestRelease/$(echo $2 | cut -d'/' -f4 | cut -d'P' -f1)T"
  commit_feature_branch=$(git log --pretty=%P -n 1  $1| awk '{print $2}')
  echo $commit_feature_branch
  if [ ! -z "$commit_feature_branch" ];
  then
    if [ `git branch -a --contains $commit_feature_branch | grep $test_release_branch` ] ;
    then
      echo "Commit is already merged in '$test_release_branch' branch."
    else 
      echo "Check failed. Commit '$commit_feature_branch' is NOT merged in test." 1>&2
    fi
  else
    echo "No parent commit found"
  fi
else
    echo "Skip check not a production release branch" 
fi
