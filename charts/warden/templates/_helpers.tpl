{{- define "warden.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "warden.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "warden.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "warden.labels" -}}
helm.sh/chart: {{ include "warden.chart" . }}
app.kubernetes.io/name: {{ include "warden.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "warden.selectorLabels" -}}
app.kubernetes.io/name: {{ include "warden.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "warden.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "warden.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Whether the chart needs to create a Secret resource.
*/}}
{{- define "warden.createSecret" -}}
{{- if or .Values.adminSecret (and (eq .Values.database.type "postgres") .Values.database.postgres.enabled (not .Values.database.external.enabled)) (and (eq .Values.database.type "postgres") .Values.database.external.enabled .Values.database.external.url (not .Values.database.external.existingSecret)) -}}
true
{{- end -}}
{{- end }}
