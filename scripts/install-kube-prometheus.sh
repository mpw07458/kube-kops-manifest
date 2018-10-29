#!/usr/bin/env bash
helm install coreos/kube-prometheus --namespace monitoring --name kube-prometheus -f prometheus-config.yaml