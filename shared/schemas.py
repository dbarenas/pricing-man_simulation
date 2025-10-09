def default_topics(project_id):
    return {
        "OCCUPATION": f"projects/{project_id}/topics/ocupacion_update",
        "FORECAST": f"projects/{project_id}/topics/forecast_demanda",
        "PRICE": f"projects/{project_id}/topics/sugerencia_precio",
        "ACTIONS": f"projects/{project_id}/topics/actions_promotions",
    }