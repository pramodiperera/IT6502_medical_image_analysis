"""Prompts for each supported medical image type.

Each prompt tells the vision model to:
  1. Confirm the image matches the selected modality (and stop if it doesn't).
  2. Classify into a fixed set of categories.
  3. Return confidence, reasoning, and key visual observations.
  4. Include a medical disclaimer.
"""

def _disclaimer(specialist: str) -> str:
    """Build the disclaimer text for a given specialist."""
    return (
        f"IMPORTANT: Always recommend review by a qualified {specialist}."
    )


CHEST_XRAY_PROMPT = f"""
You are assisting with analysis of a CHEST X-RAY (radiograph) image.

First, confirm whether the image appears to be a chest X-ray. If it is not a
chest X-ray, say so clearly and stop.

If it is a chest X-ray, classify it into exactly one of these categories:

- normal
- pneumonia
- other_abnormality

Return:

1. Classification
2. Confidence from 0 to 100
3. Explanation of the reasoning
4. Important visual observations (e.g. lung fields, opacities,
   consolidation, pleural effusion, cardiac silhouette, bones)

Do not invent information that cannot be observed from the image.

{_disclaimer("radiologist")}
"""


BRAIN_MRI_PROMPT = f"""
You are assisting with analysis of a BRAIN MRI scan image.

First, confirm whether the image appears to be a brain MRI. If it is not a
brain MRI, say so clearly and stop.

If it is a brain MRI, classify it into exactly one of these categories:

- normal
- tumor
- other_abnormality

Return:

1. Classification
2. Confidence from 0 to 100
3. Explanation of the reasoning
4. Important visual observations (e.g. symmetry of hemispheres, ventricles,
   mass effect, midline shift, abnormal signal intensity, lesions)

Do not invent information that cannot be observed from the image.

{_disclaimer("neurologist")}
"""



RETINAL_FUNDUS_PROMPT = f"""
You are assisting with analysis of a RETINAL FUNDUS (eye) photograph.

First, confirm whether the image appears to be a retinal fundus image. If it
is not a retinal fundus image, say so clearly and stop.

If it is a retinal fundus image, classify it into exactly one of these
categories:

- normal
- diabetic_retinopathy
- other_abnormality

Return:

1. Classification
2. Confidence from 0 to 100
3. Explanation of the reasoning
4. Important visual observations (e.g. optic disc, macula, blood vessels,
   microaneurysms, hemorrhages, exudates, neovascularization)

Do not invent information that cannot be observed from the image.

{_disclaimer("ophthalmologist")}
"""




# Maps the user-facing label to its prompt.
PROMPTS = {
    "Chest X-ray": CHEST_XRAY_PROMPT,
    "Brain MRI": BRAIN_MRI_PROMPT,
    "Retinal Fundus": RETINAL_FUNDUS_PROMPT,
}

# Optional emoji/icon per type for the UI.
ICONS = {
    "Chest X-ray": "🫁",
    "Brain MRI": "🧠",
    "Retinal Fundus": "👁️",
}

