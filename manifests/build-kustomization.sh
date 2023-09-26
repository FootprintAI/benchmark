#!/usr/bin/env bash
#
#
# ./build-kustomization.sh $target
target=$1
if [ "$#" -eq 1 ]
then
    echo "compile target $target"
    buildpath=overlays/$target
    echo "path: $buildpath"
    kustomize build --enable-helm --stack-trace --load-restrictor LoadRestrictionsNone $buildpath --output autogen.$target.yaml
else
    echo "incorrect format: ./build-kustomization.sh target"
fi
