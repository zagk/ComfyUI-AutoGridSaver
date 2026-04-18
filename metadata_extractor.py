# -*- coding: utf-8 -*-
import logging
import json
import re
import sys

logger = logging.getLogger("ComfyUI.MetadataExtractor")

LORA_LOADER_CLASSES = {
    "LoraLoader", "LoRALoader",
    "Lora Loader (LoraManager)",
    "Lora Stacker (LoraManager)",
    "LoraLoaderModelOnly",
    "CR Load LoRA",
    "Power Lora Loader (rgthree)",
}


class MetadataExtractor:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"images": ("IMAGE",)},
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "no_prompt",
        "seed", 
        "steps", 
        "cfg_scale", 
        "sampler", 
        "scheduler",
        "checkpoint", 
        "loras",      # ← LoRA 복구
        "size"
    )

    FUNCTION = "process_metadata"
    CATEGORY = "image/AutoGrid"
    OUTPUT_NODE = True

    def collect_loras(self, prompt_graph):
        """워크플로우에서 LoRA 정보 수집"""
        lora_list = []
        seen = set()

        for node_id, node in prompt_graph.items():
            class_type = node.get("class_type", "")
            inputs = node.get("inputs", {})

            # 1. LoraLoader 계열 노드
            if class_type in LORA_LOADER_CLASSES:
                # lora_name 방식
                if "lora_name" in inputs:
                    name = inputs.get("lora_name")
                    strength = inputs.get("strength_model", 1.0)
                    if name:
                        tag = f"<lora:{name}:{strength:.2f}>"
                        if tag not in seen:
                            seen.add(tag)
                            lora_list.append(tag)

                # text에 <lora:xxx> 직접 쓴 경우
                text_val = inputs.get("text", "")
                if isinstance(text_val, str) and "<lora:" in text_val:
                    for tag in re.findall(r"<lora:[^>]+>", text_val):
                        if tag not in seen:
                            seen.add(tag)
                            lora_list.append(tag)

                # Lora Stacker 등 __value__ 방식
                loras_field = inputs.get("loras", {})
                if isinstance(loras_field, dict) and "__value__" in loras_field:
                    for item in loras_field.get("__value__", []):
                        if isinstance(item, dict) and item.get("active", True):
                            name = item.get("name", "")
                            strength = item.get("strength", 1.0)
                            if name:
                                tag = f"<lora:{name}:{strength:.2f}>"
                                if tag not in seen:
                                    seen.add(tag)
                                    lora_list.append(tag)

        return lora_list

    def process_metadata(self, images, prompt=None, extra_pnginfo=None, id=None):
        res = {
            "seed": "N/A",
            "steps": "N/A",
            "cfg_scale": "N/A",
            "sampler": "N/A",
            "scheduler": "N/A",
            "checkpoint": "N/A",
            "loras": [],
            "size": "Unknown"
        }

        try:
            if prompt is not None:
                # ==================== KSampler 찾기 ====================
                ksampler_id = None
                for node_id, node in prompt.items():
                    if node.get("class_type") in ["KSampler", "KSamplerAdvanced"]:
                        ksampler_id = node_id
                        break

                if not ksampler_id:
                    for node_id, node in prompt.items():
                        if node.get("class_type") == "VAEDecode":
                            inputs = node.get("inputs", {})
                            samples = inputs.get("samples")
                            if isinstance(samples, list):
                                latent_id = str(samples[0])
                                latent_node = prompt.get(latent_id, {})
                                if latent_node.get("class_type") in ["KSampler", "KSamplerAdvanced"]:
                                    ksampler_id = latent_id
                                    break

                if ksampler_id:
                    ksampler = prompt.get(ksampler_id, {})
                    inputs = ksampler.get("inputs", {})

                    seed_raw = inputs.get("seed") or inputs.get("noise_seed")
                    if isinstance(seed_raw, list):
                        seed_node = prompt.get(str(seed_raw[0]), {})
                        res["seed"] = seed_node.get("inputs", {}).get("seed", "N/A")
                    elif seed_raw is not None:
                        res["seed"] = seed_raw

                    res["steps"] = inputs.get("steps", "N/A")
                    res["cfg_scale"] = inputs.get("cfg", "N/A")
                    res["sampler"] = inputs.get("sampler_name", "N/A")
                    res["scheduler"] = inputs.get("scheduler", "N/A")

                # ==================== Checkpoint 찾기 ====================
                for node_id, node in prompt.items():
                    inputs = node.get("inputs", {})
                    if "ckpt_name" in inputs:
                        res["checkpoint"] = inputs["ckpt_name"]
                    elif "unet_name" in inputs:
                        res["checkpoint"] = inputs.get("unet_name", "N/A")

                # ==================== LoRA 수집 ====================
                res["loras"] = self.collect_loras(prompt)

            # ==================== 이미지 크기 ====================
            if images is not None:
                _, H, W, _ = images.shape
                res["size"] = f"{W}x{H}"

            # no_prompt용 JSON
            no_prompt_dict = {k: v for k, v in res.items()}
            no_prompt_text = json.dumps(no_prompt_dict, indent=2, ensure_ascii=False)

            # LoRA 출력 문자열
            loras_output = ", ".join(res["loras"]) if res["loras"] else "None"

            results = (
                no_prompt_text,
                str(res["seed"]),
                str(res["steps"]),
                str(res["cfg_scale"]),
                str(res["sampler"]),
                str(res["scheduler"]),
                str(res["checkpoint"]),
                loras_output,
                str(res["size"])
            )

            return {"result": results, "ui": {"text": [no_prompt_text]}}

        except Exception as e:
            logger.exception("MetadataExtractor error")
            error_msg = f"Error: {str(e)}"
            return {"result": (error_msg,) * 9}


NODE_CLASS_MAPPINGS = {"MetadataExtractor": MetadataExtractor}
NODE_DISPLAY_NAME_MAPPINGS = {"MetadataExtractor": "Metadata Extractor zk"}