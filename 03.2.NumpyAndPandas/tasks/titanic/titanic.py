import typing as tp
import polars as pl


def male_age(df: pl.DataFrame) -> float:
    """
    Return mean age of survived men, embarked in Southampton with fare > 30
    :param df: dataframe
    :return: mean age
    """
    survived_man = df.filter((pl.col('Survived') == 1) & (pl.col('Embarked') == 'S') & (pl.col('Fare') > 30)
                             & (pl.col('Age').is_not_null()) & (pl.col('Sex') == "male"))
    temp = survived_man.select(pl.col('Age').cast(pl.Float64)).mean()
    return temp.item()

def nan_columns(df: pl.DataFrame) -> tp.Iterable[str]:
    """
    Return list of columns containing nans
    :param df: dataframe
    :return: series of columns
    """
    answer = []
    for col in df.columns:
        if df[col].is_null().any():
            answer.append(col)
    return answer


def class_distribution(df: pl.DataFrame) -> pl.Series:
    """
    Return Pclass distrubution
    :param df: dataframe
    :return: series with ratios
    """
    total_passangers = df.height
    max_pclass = df.select(pl.col('Pclass').cast(int)).max().item()
    answer = []
    for pclass in range(1, max_pclass + 1):
        answer.append(len(df.filter(pl.col('Pclass') == pclass)) / total_passangers)
    return pl.Series(answer)


def families_count(df: pl.DataFrame, k: int) -> int:
    """
    Compute number of families with more than k members
    :param df: dataframe,
    :param k: number of members,
    :return: number of families
    """
    df_with_surnames = df.with_columns(pl.col('Name').str.split(',').list.first().alias('Surname'))
    counted_surnames = df_with_surnames.group_by('Surname').agg(pl.len().alias('Count'))
    answer  = counted_surnames.filter(pl.col('Count') > k)
    return answer.height



def mean_price(df: pl.DataFrame, tickets: tp.Iterable[str]) -> float:
    """
    Return mean price for specific tickets list
    :param df: dataframe,
    :param tickets: list of tickets,
    :return: mean fare for this tickets
    """
    ticket_list = df.filter(pl.col('Ticket').is_in(list(tickets)))
    return ticket_list.select(pl.col('Fare').cast(float)).mean().item()

def max_size_group(df: pl.DataFrame, columns: list[str]) -> tp.Iterable[tp.Any]:
    """
    For given set of columns compute most common combination of values of these columns
    :param df: dataframe,
    :param columns: columns for grouping,
    :return: list of most common combination
    """
    selected_df = df.select(columns).drop_nulls()
    grouped_df = selected_df.group_by(columns).agg(pl.len().alias('Count'))
    return grouped_df.top_k(1, by = 'Count').drop('Count').row(0)

def dead_lucky(df: pl.DataFrame) -> float:
    """
    Compute dead ratio of passengers with lucky tickets.
    A ticket is considered lucky when it contains an even number of digits in it
    and the sum of the first half of digits equals the sum of the second part of digits
    ex:
    lucky: 123222, 2671, 935755
    not lucky: 123456, 62869, 568290
    :param df: dataframe,
    :return: ratio of dead lucky passengers
    """
    died = 0
    all = 0
    for line in df.iter_rows(named = True):
        ticket_str = line['Ticket']
        if str.isdigit(ticket_str) and len(ticket_str) % 2 == 0:
            temp1 = 0
            temp2 = 0
            for ind in range(len(ticket_str)):
                if ind < len(ticket_str) / 2:
                    temp1 += int(ticket_str[ind])
                else:
                    temp2 += int(ticket_str[ind])
            if temp1 == temp2:
                all += 1
                if line['Survived'] == 0:
                    died += 1
    return died/all
