# Timelapse Consolidator

Create a single timelapse video from multiple captures, ignoring night shots

- 100% vibecode, ceated by Claude Sonnet 4.5
- Prompt: [prompt.md](prompt.md)
- Doc: [doc.md](doc.md)

That was a difficult bugfix:
```
use ffmpeg, do not use -vsync arg
```
## The Story

My colleague has 200+ days of security camera footage covering his property, during which time their house was built.

Each video file contains roughly 12 hours, with the entire set being around 30 GB (or 300? I don't know the exact number, but it's a massive amount). Some image processing is also needed: the nighttime images need to be filtered out.

He's been wanting to make a timelapse from it for a long time, but couldn't find a suitable automation tool for it. Using normal video editors would be unmanageably labor-intensive, especially filtering out the nighttime footage.

## Method

I left a lot to the AI, except: I insisted it not use OpenCV (that's why I specified ffmpeg), and since the programs call each other, I had to explicitly describe the CLI arguments for each program.

For the nighttime filtering, I first wanted to do it based on lightness, but the camera's night mode is too bright; however, it's black and white, so I filter the nighttime recordings based on saturation.

The biggest difficulty was a problematic ffmpeg argument causing a weird error, required to dig into ffmpeg args.

See (AI-generated) [doc.md](doc.md) for some more details.

## Improvements

It could be parallelized or use a native platform for faster image processing, but since it's only going to run once, speed isn't really an issue.
