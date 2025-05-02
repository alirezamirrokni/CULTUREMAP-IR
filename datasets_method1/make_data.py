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
        "name": item.get("name", ""),
        "images": item.get("images", []),
    }
    if extra_fields:
        task.update(extra_fields)
    output.append(task)
    item_id += 1

for filename in dataset_filenames:
    filepath = os.path.join(base_dir, filename)

    if not os.path.exists(filepath):
        print(f"❌ فایل پیدا نشد: {filepath}")
        continue

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ فایل بارگذاری شد: {filename}")
    except Exception as e:
        print(f"❌ خطا در خواندن {filename}: {e}")
        continue

    datasets = data if isinstance(data, list) else [data]

    for dataset in datasets:
        province = dataset.get("province", "نامشخص")

        # ویژگی‌های جغرافیایی
        for feature in dataset.get("geographical_features", []):
            section = feature.get("name", "")
            for item in feature.get("items", []):
                add_item("geographical_feature", section, item, province)

        # جاذبه‌های گردشگری
        for place in dataset.get("tourist_attractions", []):
            add_item("tourist_attraction", place.get("name", ""), place, province, {
                "year_built": place.get("year_built", ""),
                "constructor": place.get("constructor", ""),
                "architect": place.get("architect", ""),
                "description": place.get("description", "")
            })

        # پوشش گیاهی
        for plant in dataset.get("vegetation", []):
            add_item("vegetation", "پوشش گیاهی", {"name": plant, "images": []}, province)

        # توپوگرافی
        for topo in dataset.get("topography", []):
            desc = "، ".join(topo.get("description", [])) if topo.get("description") else ""
            add_item("topography", topo.get("name", ""), {"name": topo.get("name", ""), "images": []}, province, {
                "description": desc
            })

# مسیر خروجی
output_file = os.path.join(base_dir, "labelstudio_all_provinces.json")

# ذخیره خروجی
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n🎉 خروجی ذخیره شد: {output_file}")
print(f"📦 تعداد نمونه‌ها: {len(output)}")
