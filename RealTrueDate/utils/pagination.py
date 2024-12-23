from rest_framework.pagination import PageNumberPagination


def paginate_queryset(queryset, request, page_size=10):
    """
    Paginate a queryset and return paginated data and metadata.

    :param queryset: The queryset to be paginated (Django QuerySet or list).
    :param request: The incoming request object (used to get page number).
    :param page_size: Number of items per page (default is 10). If 0, returns no data.
    :return: A dictionary containing paginated data and metadata (count, current page count, current page, start record, end record).
    """
    # Handle zero page size
    if page_size == 0:
        return {
            'data': [],  # Empty data for zero page size
            'count': len(queryset),  # Total count
            'current_page_count': 0,
            'current_page': 0,  # Indicate no page
            'start_record': 0,
            'end_record': 0,
        }

    # Handle lists as well as QuerySets
    if not hasattr(queryset, 'count'):  # Not a QuerySet, treat as a list
        queryset = list(queryset)

    # Instantiate DRF paginator
    paginator = PageNumberPagination()
    paginator.page_size = page_size

    # Paginate queryset
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    # Calculate start and end records
    start_record = (paginator.page.number - 1) * paginator.page_size + 1
    end_record = start_record + len(paginated_queryset) - 1

    # Return paginated data and metadata
    return {
        'data': paginated_queryset,
        'count': paginator.page.paginator.count,  # Total item count
        'current_page_count': len(paginated_queryset),  # Items on the current page
        'current_page': paginator.page.number,  # Current page number
        'total_pages': paginator.page.paginator.num_pages,  # Total pages
        'start_record': start_record,  # Starting record number for the page
        'end_record': end_record,  # Ending record number for the page
    }

def paginate_and_serialize(queryset, request, serializer_class, page_size=10):
    """
    Paginate and serialize a queryset.

    :param queryset: The queryset to be paginated and serialized.
    :param request: The request object (to fetch query params like page number).
    :param serializer_class: The serializer class for serializing the queryset data.
    :param page_size: Number of items per page (default is 10).
    :return: A dictionary containing serialized data and pagination metadata.
    """
    # Handle zero page size
    if page_size == 0:
        return {
            'data': [],  # Empty data
            'count': len(queryset),  # Total item count
            'current_page_count': 0,
            'current_page': 0,
            'total_pages': 0,
            'start_record': 0,
            'end_record': 0,
        }

    # If queryset is not a QuerySet, convert it to a list
    if not hasattr(queryset, 'count'):  # Not a QuerySet
        queryset = list(queryset)

    # Initialize DRF paginator
    paginator = PageNumberPagination()
    paginator.page_size = page_size

    # Paginate queryset
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    # Serialize paginated data
    serialized_data = serializer_class(paginated_queryset, many=True).data

    # Calculate start and end records
    start_record = (paginator.page.number - 1) * page_size + 1
    end_record = start_record + len(paginated_queryset) - 1

    # Return serialized data and pagination metadata
    return {
        'data': serialized_data,
        'count': paginator.page.paginator.count,  # Total item count
        'current_page_count': len(paginated_queryset),  # Items on the current page
        'current_page': paginator.page.number,  # Current page number
        'total_pages': paginator.page.paginator.num_pages,  # Total pages
        'start_record': start_record,  # Start record index
        'end_record': end_record,  # End record index
    }

