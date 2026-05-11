import json
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from src.config import AppConfig
from src.models import TimelineClip
from src.resolve_script_template import build_template


def export_fcpxml_timeline(output_dir: Path, timeline_plan: list[TimelineClip], config: AppConfig) -> None:
    fps = config.fps
    fcpxml = ET.Element("fcpxml", version="1.5")
    resources = ET.SubElement(fcpxml, "resources")
    
    format_id = "r1"
    frame_duration = f"1/{fps}s"
    ET.SubElement(resources, "format", id=format_id, name=f"FFVideoFormat1080p{fps}", frameDuration=frame_duration, width="1920", height="1080")
    
    asset_map = {} 
    asset_idx = 2
    
    for clip in timeline_plan:
        if clip.image_path and clip.image_path not in asset_map:
            asset_id = f"r{asset_idx}"
            asset_idx += 1
            asset_map[clip.image_path] = asset_id
            abs_img = Path(clip.image_path).resolve()
            src_url = "file:///" + urllib.parse.quote(abs_img.as_posix().replace('\\', '/'), safe=':/')
            ET.SubElement(resources, "asset", id=asset_id, name=abs_img.name, src=src_url, hasVideo="1", hasAudio="0")
            
        if clip.audio_path and clip.audio_path not in asset_map:
            asset_id = f"r{asset_idx}"
            asset_idx += 1
            asset_map[clip.audio_path] = asset_id
            abs_aud = Path(clip.audio_path).resolve()
            src_url = "file:///" + urllib.parse.quote(abs_aud.as_posix().replace('\\', '/'), safe=':/')
            ET.SubElement(resources, "asset", id=asset_id, name=abs_aud.name, src=src_url, hasVideo="0", hasAudio="1")

    library = ET.SubElement(fcpxml, "library")
    event = ET.SubElement(library, "event", name="AI Video Pipeline")
    project = ET.SubElement(event, "project", name=config.timeline_name)
    sequence = ET.SubElement(project, "sequence", format=format_id)
    spine = ET.SubElement(sequence, "spine")
    
    for clip in timeline_plan:
        duration_frames = int(round(clip.duration_seconds * fps))
        duration_str = f"{duration_frames}/{fps}s"
        
        img_asset_id = asset_map.get(clip.image_path)
        aud_asset_id = asset_map.get(clip.audio_path)
        
        if img_asset_id:
            video_clip = ET.SubElement(spine, "asset-clip", 
                                       name=Path(clip.image_path).name,
                                       ref=img_asset_id,
                                       duration=duration_str,
                                       format=format_id)
                                       
            if aud_asset_id:
                audio_clip = ET.SubElement(video_clip, "asset-clip",
                                           name=Path(clip.audio_path).name,
                                           ref=aud_asset_id,
                                           duration=duration_str,
                                           lane="-1",
                                           offset="0s")
                                           
    xml_str = ET.tostring(fcpxml, encoding="UTF-8", xml_declaration=True).decode("utf-8")
    final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n' + xml_str.split('?>', 1)[-1].strip()
    
    fcpxml_path = output_dir / "timeline_for_davinci.fcpxml"
    fcpxml_path.write_text(final_xml, encoding="utf-8")


def export_resolve_import_plan(output_dir: Path, timeline_plan: list[TimelineClip], config: AppConfig) -> None:
    payload = {
        "project_name": config.project_name,
        "timeline_name": config.timeline_name,
        "video_track": 1,
        "audio_track": 1,
        "fps": config.fps,
        "clips": [clip.to_dict() for clip in timeline_plan],
        "next_step": [
            "You can use timeline_for_davinci.fcpxml to import into DaVinci Resolve Free.",
            "In DaVinci Resolve: File -> Import -> Timeline -> Select timeline_for_davinci.fcpxml"
        ],
    }
    path = output_dir / "resolve_import_plan.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Tạo file mẫu Python cũ (cho bản Studio)
    template_path = output_dir / "resolve_import_template.py"
    template_path.write_text(build_template(path), encoding="utf-8")
    
    # TẠO FILE FCPXML cho bản MIỄN PHÍ
    export_fcpxml_timeline(output_dir, timeline_plan, config)
