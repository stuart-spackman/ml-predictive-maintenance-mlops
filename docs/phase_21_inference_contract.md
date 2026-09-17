# Phase 2.1 — Inference Contract

## Purpose

Given the raw observed history of one FD001-style engine through its current
cycle, generate one RUL prediction for the latest eligible cycle using the
locked Phase 1 model.

## Input contract

The Phase 2.1 MVP accepts:

- one engine per inference request,
- raw operating-setting and sensor observations,
- sequential engine history through the current cycle,
- at least 10 observed cycles.

The caller does not supply:

- RUL targets,
- temporal lag features,
- rolling statistics,
- model-ready feature vectors.

## Output contract

A successful inference produces:

- engine identifier,
- current/latest observed cycle,
- predicted remaining useful life.

## Internal responsibilities

The inference pipeline owns:

- validation,
- temporal feature construction,
- feature selection and ordering,
- locked model loading,
- prediction generation.

## Phase 2.1 non-goals

The initial inference pipeline will not:

- retrain models,
- tune hyperparameters,
- select candidate models,
- accept multiple engines in one prediction request,
- predict future sensor values,
- update the model online,
- expose an HTTP API,
- provide the Streamlit user interface.

HTTP serving belongs to Phase 2.2.

Containerization, CI, and the demo layer belong to later Phase 2 phases.