# Skill: Media Pipeline & Upload Security

Product images:
- 1–10 per product
- one primary
- explicit sort order

Validate:
- extension
- MIME
- actual content
- file size
- dimensions

Optimize:
- WebP/AVIF where practical
- responsive variants
- thumbnails
- lazy loading
- alt text

Videos:
- allowlisted formats
- size/duration limits
- safe storage
- no executable delivery
- transcode asynchronously only if truly needed

Storage:
- prefer object storage in production
- separate code/static/media
- randomized server filenames
- never build file paths from user input

Consider stripping EXIF/GPS metadata.

No fake product images. Use a controlled Coming Soon placeholder when needed.
