from click import option, INT, STRING, Path


d_less = option("--less", is_flag=True, help="Show less like output.")
d_offset = option("-o", "--offset", type=INT, default=0, help="The initial index from which to return the results.")
d_limit = option("-l", "--limit", type=INT, default=20, help="Number of results to return per page.")
d_localize = option("--localize", is_flag=True, help="Convert UTC datetime to local timezone.")
d_filter = option(
    "-f",
    "--filter",
    "parameter_filters",
    type=(STRING, STRING),
    multiple=True,
    help="Filter results using returned parameters (for example `id 1`, `name value`).",
)
d_save_report = option(
    "-f", "--file", type=Path(exists=True), default="/tmp", help="File to save the report to (default is /tmp)."
)


def common_list_decorators(function):
    function = d_less(function)
    function = d_offset(function)
    function = d_limit(function)
    function = d_localize(function)
    function = d_filter(function)
    return function
