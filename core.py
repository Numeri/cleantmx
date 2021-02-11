from typing import Callable, Optional, Text, Tuple, Union

__all__ = ['FilterType', 'Unit', 'ParallelFilterType', 'applySingleFilters', 'applyFilters']

FilterType = Callable[[Text], Optional[Text]]
Unit = Tuple[Text, Text]
ParallelFilterType = Callable[[Unit], Optional[Unit]]

def applySingleFilters(*filters: FilterType) -> FilterType:
    def _applySingleFilters(text : Text) -> Optional[Text]:
        for f in filters:
            text = f(text)
            if text is None:
                return None
        return text

    return _applySingleFilters

def applyFilters(*filters : Union[FilterType, ParallelFilterType, Tuple[FilterType, FilterType]]) -> ParallelFilterType:
    def _applyFilters(unit : Unit) -> Optional[Unit]:
        source, target = unit
        for f in filters:
            if type(f) is tuple:
                source_filter, target_filter = f
                source = source_filter(source)
                target = target_filter(target)
            elif f.__annotations__['return'] is Optional[Unit]:
                unit = f((source, target))
                if unit is None:
                    return None
                source, target = unit
            else:
                source = f(source)
                target = f(target)

            if source is None or target is None:
                return None
        return source, target

    return _applyFilters

