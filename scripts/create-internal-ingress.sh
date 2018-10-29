#!/usr/bin/env bash
helm install stable/nginx-ingress -f nginx-ingress-internal.yaml --namespace nginx-ingress-internal