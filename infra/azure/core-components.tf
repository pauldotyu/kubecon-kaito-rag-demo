resource "helm_release" "argo_cd" {
  name             = "argocd-release"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = "8.6.3"
  namespace        = "argocd"
  create_namespace = true
}

resource "helm_release" "argo_workflows" {
  name             = "argoworkflows-release"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-workflows"
  version          = "0.45.27"
  namespace        = "argo"
  create_namespace = true

  depends_on = [helm_release.argo_cd]
}

resource "helm_release" "istio_base" {
  name             = "istio-base"
  chart            = "oci://gcr.io/istio-testing/charts/base"
  version          = "1.28-alpha.2d5fc65b386ac3c3eff28aee4040dce37923b9b7"
  namespace        = "istio-system"
  create_namespace = true

  depends_on = [helm_release.argo_workflows]
}

resource "helm_release" "istiod" {
  name             = "istiod"
  chart            = "oci://gcr.io/istio-testing/charts/istiod"
  version          = "1.28-alpha.2d5fc65b386ac3c3eff28aee4040dce37923b9b7"
  namespace        = "istio-system"
  create_namespace = false

  set = [
    {
      name  = "pilot.env.ENABLE_GATEWAY_API_INFERENCE_EXTENSION"
      value = "true"
    },
    {
      name  = "tag"
      value = "1.28-alpha.2d5fc65b386ac3c3eff28aee4040dce37923b9b7"
    },
    {
      name  = "hub"
      value = "gcr.io/istio-testing"
    }
  ]

  depends_on = [helm_release.istio_base]
}

resource "helm_release" "body_based_router" {
  name             = "body-based-router"
  chart            = "oci://registry.k8s.io/gateway-api-inference-extension/charts/body-based-routing"
  version          = "v1.0.0"
  namespace        = "istio-system"
  create_namespace = false

  set = [
    {
      name  = "provider.name"
      value = "istio"
    }
  ]

  depends_on = [helm_release.istiod]
}
