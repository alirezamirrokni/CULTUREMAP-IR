import json
import os

dataset_filenames = [
    "Isfahan.json",
    "Bushehr.json",
    "Chaharmahal and Bakhtiari.json",
    "Fars.json",
    "Kohgiluyeh and Boyer-Ahmad.json",
    "Hormozgan.json"
]

base_dir = os.path.dirname(os.path.abspath(__file__))
output = []
item_id = 1

def add_item(category, section, item, province, extra_fields=None):
    global item_id
    task = {
        "id": f"{category}_{item_id:05}",
        "province": province,
        "category": category,
        "section": section,
        "name": item.get("name", item.get("type", "")),
        "images": item.get("images", []),
    }
    if extra_fields:
        task.update(extra_fields)
    output.append(task)
    item_id += 1

for filename in dataset_filenames:
    filepath = os.path.join(base_dir, filename)

    if not os.path.exists(filepath):
        print(f"❌ فایل پیدا نشد: {filename}")
        continue

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ فایل بارگذاری شد: {filename}")
    except Exception as e:
        print(f"❌ خطا در خواندن {filename}: {e}")
        continue

    dataset = data
    province = dataset.get("location", {}).get("province", "نامشخص")

    # ویژگی‌های جغرافیایی: دو نوع ساختار ممکن
    geo = dataset.get("geographical_features", {})
    if isinstance(geo, list):  # For datasets like Bushehr, Kohgiluyeh
        for feature in geo:
            section = feature.get("name", "")
            items = feature.get("description", [])
            for item in items:
                if isinstance(item, str):
                    add_item("geographical_feature", section, {"name": item, "images": []}, province)
                elif isinstance(item, dict):
                    add_item("geographical_feature", section, item, province)
    elif isinstance(geo, dict):  # For datasets like Isfahan
        for section, items in geo.items():
            if section != "vegetation":
                for item in items:
                    add_item("geographical_feature", section, item, province)

        for veg in geo.get("vegetation", []):
            add_item("vegetation", veg.get("type", "پوشش گیاهی"), {"name": veg.get("type", ""), "images": []}, province, {
                "species": veg.get("species", []),
                "quality": veg.get("quality", [])
            })

    # topography
    for topo in dataset.get("topography", []):
        add_item("topography", topo.get("name", ""), {"name": topo.get("name", ""), "images": []}, province, {
            "description": topo.get("description", [])
        })

    # natural_resources
    for res in dataset.get("natural_resources", []):
        add_item("natural_resource", res.get("name", ""), {"name": res.get("name", ""), "images": []}, province, {
            "description": res.get("description", [])
        })

    # environmental_issues
    for section, issues in dataset.get("environmental_issues", {}).items():
        for issue in issues:
            add_item("environmental_issue", section, {"name": issue, "images": []}, province)

    # climate change impacts
    for impact in dataset.get("climate_change_impacts", []):
        add_item("climate_change_impact", "climate", {"name": impact, "images": []}, province)

    # tourist attractions
    for place in dataset.get("tourist_attractions", []):
        add_item("tourist_attraction", "جاذبه گردشگری", place, province, {
            "year_built": place.get("year_built", ""),
            "constructor": place.get("constructor", ""),
            "architect": place.get("architect", ""),
            "description": place.get("description", "")
        })

    # economic_capabilities
    for section, subcats in dataset.get("economic_capabilities", {}).items():
        if isinstance(subcats, dict):
            for sub, items in subcats.items():
                if isinstance(items, list):
                    for item in items:
                        add_item("economic_capability", f"{section} - {sub}", {"name": item, "images": []}, province)
                else:
                    add_item("economic_capability", f"{section} - {sub}", {"name": str(items), "images": []}, province)

    # human_geography
    for section, value in dataset.get("human_geography", {}).items():
        if isinstance(value, dict):
            for sub, val in value.items():
                if isinstance(val, list):
                    for item in val:
                        add_item("human_geography", f"{section} - {sub}", {"name": item, "images": []}, province)
                else:
                    add_item("human_geography", f"{section} - {sub}", {"name": str(val), "images": []}, province)
        else:
            add_item("human_geography", section, {"name": str(value), "images": []}, province)

    # culture_and_customs
    for section, items in dataset.get("culture_and_customs", {}).items():
        for item in items:
            add_item("culture_and_custom", section, {"name": item, "images": []}, province)

    # historical_heritage
    for section, items in dataset.get("historical_heritage", {}).items():
        for item in items:
            add_item("historical_heritage", section, {"name": item, "images": []}, province)

# ذخیره خروجی نهایی
output_file = os.path.join(base_dir, "labelstudio_dataset_full.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n🎯 خروجی نهایی ذخیره شد در: {output_file}")
print(f"📦 تعداد نمونه‌ها: {len(output)}")
