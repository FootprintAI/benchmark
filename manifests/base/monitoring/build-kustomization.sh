#!/usr/bin/env bash

# NOTE: requires kustomization 4+
# https://github.com/kubernetes-sigs/kustomize/tree/kustomize/v4.5.7
kustomize4.5.7 build --enable-helm base > autogen.base.yaml
