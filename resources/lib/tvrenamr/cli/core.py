#!/usr/bin/env python

from __future__ import absolute_import

import functools
import logging
import os
import sys

from tvrenamr import __version__, errors
from tvrenamr.cli.helpers import (build_file_list, get_config, start_dry_run,
                                  stop_dry_run)
from tvrenamr.main import File, TvRenamr

log = logging.getLogger('CLI')

def rename(config, canonical, debug, dry_run, episode,  # pylint: disable-msg=too-many-arguments
           ignore_filelist, log_file, log_level, name,  # pylint: disable-msg=too-many-arguments
           no_cache, output_format, organise, partial,  # pylint: disable-msg=too-many-arguments
           quiet, recursive, rename_dir, regex, season,  # pylint: disable-msg=too-many-arguments
           show, show_override, specials, symlink, the,  # pylint: disable-msg=too-many-arguments
           paths):  # pylint: disable-msg=too-many-arguments

    logger = functools.partial(log.log, 26)

    if dry_run or debug:
        start_dry_run(logger)

    if not paths:
        paths = [os.getcwd()]

    for current_dir, filename in build_file_list(paths, recursive, ignore_filelist):
        try:
            tv = TvRenamr(current_dir, debug, dry_run, symlink, no_cache)

            _file = File(**tv.extract_details_from_file(
                filename,
                user_regex=regex,
                partial=partial,
            ))
            # TODO: Warn setting season & episode will override *all* episodes
            _file.user_overrides(show, season, episode)
            _file.safety_check()

            conf = get_config(config)

            for ep in _file.episodes:
                canonical = conf.get(
                    'canonical',
                    _file.show_name,
                    default=ep.file_.show_name,
                    override=canonical
                )

                # TODO: Warn setting name will override *all* episodes
                ep.title = tv.retrieve_episode_title(
                    ep,
                    canonical=canonical,
                    override=name,
                )

                # TODO: make this a sanitisation method on ep?
                ep.title = ep.title.replace('/', '-')

            show = conf.get_output(_file.show_name, override=show_override)
            the = conf.get('the', show=_file.show_name, override=the)
            _file.show_name = tv.format_show_name(show, the=the)

            _file.set_output_format(conf.get(
                'format',
                _file.show_name,
                default=_file.output_format,
                override=output_format
            ))

            organise = conf.get(
                'organise',
                _file.show_name,
                default=False,
                override=organise
            )
            rename_dir = conf.get(
                'renamed',
                _file.show_name,
                default=current_dir,
                override=rename_dir
            )
            specials_folder = conf.get(
                'specials_folder',
                _file.show_name,
                default='Season 0',
                override=specials,
            )
            path = tv.build_path(
                _file,
                rename_dir=rename_dir,
                organise=organise,
                specials_folder=specials_folder,
            )

            tv.rename(filename, path)
        except errors.NetworkException:
            if dry_run or debug:
                stop_dry_run(logger)
            sys.exit(1)
        except (AttributeError,
                errors.EmptyEpisodeTitleException,
                errors.EpisodeNotFoundException,
                errors.IncorrectRegExpException,
                errors.InvalidXMLException,
                errors.MissingInformationException,
                errors.OutputFormatMissingSyntaxException,
                errors.PathExistsException,
                errors.ShowNotFoundException,
                errors.UnexpectedFormatException) as e:
            continue
        except Exception as e:
            if debug:
                # In debug mode, show the full traceback.
                raise
            for msg in e.args:
                log.critical('Error: %s', msg)
            sys.exit(1)

        # if we're not doing a dry run add a blank line for clarity
        if not (debug and dry_run):
            log.info('')

    if dry_run or debug:
        stop_dry_run(logger)
