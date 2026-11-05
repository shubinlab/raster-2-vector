# Security

Raster/vector files can contain untrusted input. The restricted SVG renderer refuses embedded raster images, external URLs, doctypes, unusual tags, and scripts. It is not intended as a hardened sandbox for hostile SVG or malformed image exploits.

Do not commit credentials, private artwork, or user-specific inputs. Review the skill instructions and Dockerfile before running them. Mount the smallest practical local folder into Docker.

Please report vulnerabilities privately to the repository owner using GitHub (prefer the private vulnerability reporting feature if enabled). Do not post working exploits publicly before coordination.
