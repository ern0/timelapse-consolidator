# The prompt

```
write python program extract_iframes_from_mp4.py
open mp4 file specified as arg --file
exctract every 20th iframe, specified --nth arg
save jpgs into working directory, specified --workdir arg, create if not exists
before processing delete all files from working directory
use ffmpeg
add shebang

write python program delete_dark_images.py
scan working directory specified --workdir arg
process each jpeg file
calculate median pixel saturation
if saturatuion less than 5% specified --saturation arg, delete image
use Pillow library
add shebang

write python program collect_selected_images.py
process all jpg files in working directory, specified --workdir arg, abc order
append jpg files to mp4 result, specified --result arg
append to existing mp4 result if exists
use 25 fps
use ffmpeg, do not use -vsync arg

add shebang

write python program process.py
process data directory recursively abc order, specified --source arg
nth iframe is specified by --nth arg
workdir is specified by --workdir arg
result is specified by --result arg
process each mp4 with external program: extract_iframes_from_mp4.py, args: --file actual file, --nth "nth_iframe" passed from arg, --result is passed from "result" arg
then call external program delete_dark_images.py with --workdir "result"
then call collect_selected_images.py
delete "result" before processing
add shebang

create single file install.py, it saves all script files
```
