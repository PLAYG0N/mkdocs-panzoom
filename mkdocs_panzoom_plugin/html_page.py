import json

def create_meta_tags(config):
    json_content = json.dumps({"selectors": config.get("selectors"),
                               "initial_zoom_level": config.get("initial_zoom_level", 1.0)})
    return f"""<meta name="panzoom-theme" content="{config.get('theme').name}">
<meta name="panzoom-data" content='{json_content}'>"""