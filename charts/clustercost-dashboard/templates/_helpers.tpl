{{- define "clustercost-dashboard.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "clustercost-dashboard.fullname" -}}
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

{{- define "clustercost-dashboard.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "clustercost-dashboard.labels" -}}
helm.sh/chart: {{ include "clustercost-dashboard.chart" . }}
app.kubernetes.io/name: {{ include "clustercost-dashboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "clustercost-dashboard.selectorLabels" -}}
app.kubernetes.io/name: {{ include "clustercost-dashboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "clustercost-dashboard.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "clustercost-dashboard.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "clustercost-dashboard.defaultAgentToken" -}}
{{- if .Values.config.defaultAgentToken }}
{{- .Values.config.defaultAgentToken }}
{{- else }}
{{- $secret := (lookup "v1" "Secret" .Release.Namespace (include "clustercost-dashboard.fullname" .) ) }}
{{- if $secret }}
{{- index $secret.data "config.yaml" | b64dec | fromYaml | get "defaultAgentToken" }}
{{- else }}
{{- randAlphaNum 32 }}
{{- end }}
{{- end }}
{{- end }}
