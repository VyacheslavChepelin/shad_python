import typing as tp


def reformat_git_log(inp: tp.IO[str], out: tp.IO[str]) -> None:
    """Reads git log from `inp` stream, reformats it and prints to `out` stream

    Expected input format: `<sha-1>\t<date>\t<author>\t<email>\t<message>`
    Output format: `<first 7 symbols of sha-1>.....<message>`
    """
    s  =inp.readline()
    while s != '':
        s = s.split('\t')
        out.write(s[0][:7])
        out.write(s[len(s) - 1].rjust(74 , '.'))
        # out.write('\n')
        s = inp.readline()

