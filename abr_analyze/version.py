name = "abr_analyze"
version_info = (0, 1, 0)  # (major, minor, patch)
dev = True

version = "{v}{dev}".format(v='.'.join(str(v) for v in version_info),
                            dev='.dev0' if dev else '')
