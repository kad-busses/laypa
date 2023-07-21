#!/bin/bash
# Created by argbash-init v2.10.0
# ARG_POSITIONAL_SINGLE([laypa_dir],[Directory of the Laypa code],[])
# ARG_DEFAULTS_POS([])
# ARG_HELP([<Build script for Laypa docker>])
# ARGBASH_GO()
# needed because of Argbash --> m4_ignore([
### START OF CODE GENERATED BY Argbash v2.10.0 one line above ###
# Argbash is a bash code generator used to get arguments parsing right.
# Argbash is FREE SOFTWARE, see https://argbash.io for more info


die()
{
	local _ret="${2:-1}"
	test "${_PRINT_HELP:-no}" = yes && print_help >&2
	echo "$1" >&2
	exit "${_ret}"
}


begins_with_short_option()
{
	local first_option all_short_options='h'
	first_option="${1:0:1}"
	test "$all_short_options" = "${all_short_options/$first_option/}" && return 1 || return 0
}

# THE DEFAULTS INITIALIZATION - POSITIONALS
_positionals=()
_arg_laypa_dir=
# THE DEFAULTS INITIALIZATION - OPTIONALS


print_help()
{
	printf '%s\n' "<Build script for Laypa docker>"
	printf 'Usage: %s [-h|--help] <laypa_dir>\n' "$0"
	printf '\t%s\n' "<laypa_dir>: Directory of the Laypa code"
	printf '\t%s\n' "-h, --help: Prints help"
}


parse_commandline()
{
	_positionals_count=0
	while test $# -gt 0
	do
		_key="$1"
		case "$_key" in
			-h|--help)
				print_help
				exit 0
				;;
			-h*)
				print_help
				exit 0
				;;
			*)
				_last_positional="$1"
				_positionals+=("$_last_positional")
				_positionals_count=$((_positionals_count + 1))
				;;
		esac
		shift
	done
}


handle_passed_args_count()
{
	local _required_args_string="'laypa_dir'"
	test "${_positionals_count}" -ge 1 || _PRINT_HELP=yes die "FATAL ERROR: Not enough positional arguments - we require exactly 1 (namely: $_required_args_string), but got only ${_positionals_count}." 1
	test "${_positionals_count}" -le 1 || _PRINT_HELP=yes die "FATAL ERROR: There were spurious positional arguments --- we expect exactly 1 (namely: $_required_args_string), but got ${_positionals_count} (the last one was: '${_last_positional}')." 1
}


assign_positional_args()
{
	local _positional_name _shift_for=$1
	_positional_names="_arg_laypa_dir "

	shift "$_shift_for"
	for _positional_name in ${_positional_names}
	do
		test $# -gt 0 || break
		eval "$_positional_name=\${1}" || die "Error during argument parsing, possibly an Argbash bug." 1
		shift
	done
}

parse_commandline "$@"
handle_passed_args_count
assign_positional_args 1 "${_positionals[@]}"

# OTHER STUFF GENERATED BY Argbash

### END OF CODE GENERATED BY Argbash (sortof) ### ])
# [ <-- needed because of Argbash

# echo "CURRENTLY NOT WORKING, MICROMAMBA Package cache error: https://github.com/mamba-org/mamba/issues/2167" && exit 1

LAYPA="$(realpath $_arg_laypa_dir)"

if [[ ! -d $LAYPA ]]; then
    echo "Can't build because laypa dir (${LAYPA}) is missing"
    exit 1
fi

docker rmi loghi/docker.laypa

echo "Change to directory of script..."
DIR_OF_SCRIPT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR_OF_SCRIPT

echo "Copy files for building docker..."
cp -r -T $LAYPA/ laypa.micromamba

# Checkout to make sure you are not on dev branch
cd laypa.micromamba
git checkout main
# git checkout dev
cd ..

echo "Building docker image..."
# docker build --squash --no-cache . -t loghi/docker.laypa
docker build --no-cache . -t loghi/docker.laypa -f Dockerfile.micromamba

rm -rf laypa.micromamba
docker system prune -f
# ] <-- needed because of Argbash
