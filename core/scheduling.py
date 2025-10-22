"""
Scheduling engine for flash card review timing.

This module handles scheduling logic for flash cards, including:
- Schedule evaluation and event generation
- Conflict resolution
- Priority-based scheduling
- Performance-based interval adjustments
"""

from __future__ import annotations

import datetime
import random
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

import logging
from database.models.flash_card import FlashCard
from database.models import FlashCard
from database.models.schedule import Schedule, Scope, FrequencyMode, ScheduledEvent, EventStatus


logger = logging.getLogger(__name__)


def get_flash_cards(
    session: Session,
    category_uuid: Optional[UUID] = None
) -> List[FlashCard]:
    """
    Get flash cards, optionally filtered by category.

    Args:
        session: The database session to use
        category_uuid: Optional UUID of category to filter by.
            If None, returns cards from all categories.

    Returns:
        List of FlashCard objects matching the filter criteria.

    Examples:
        # Get all flash cards
        all_cards = get_flash_cards(session)

        # Get cards from specific category
        category_cards = get_flash_cards(session, category_uuid)
    """
    query = select(FlashCard).where(FlashCard.active == True)
    if category_uuid is not None:
        query = query.where(FlashCard.category_uuid == category_uuid)
    return list(session.execute(query).scalars().all())


def calculate_minutes_in_schedule_window(schedule: 'Schedule') -> int:
    """
    Calculates the total number of minutes available within the schedule's time window.

    Args:
        schedule: The Schedule object containing the start_hour and end_hour attributes.

    Returns:
        The total number of minutes between the start and end hours.
    """
    return (schedule.end_hour - schedule.start_hour) * 60


def distribute_ordered_occurrences(schedule: Schedule, daily_occurrences: List[int]) -> Dict[str, int]:
    """Distribute daily occurrences in order across allowed days.
    
    Takes a list of occurrence counts and assigns them to allowed days
    in order. The list length must match the number of allowed days.
    
    Args:
        schedule: Schedule object containing allowed days configuration
        daily_occurrences: List of occurrence counts, one for each allowed day.
                          Must have same length as number of allowed days.
                         
    Returns:
        Dictionary with day abbreviations as keys (e.g., 'Mon', 'Tue')
        and number of occurrences as values
        
    Example:
        # For a schedule allowing Mon,Wed,Fri with [2,3,1] occurrences
        distribute_ordered_occurrences(schedule, [2,3,1])
        # Returns exactly: {'Mon': 2, 'Wed': 3, 'Fri': 1}
        
    Raises:
        ValueError: If length of daily_occurrences doesn't match number
                   of allowed days
    """
    # Get list of allowed days from schedule
    allowed_days = schedule.allowed_days.split(',')
    num_allowed_days = len(allowed_days)
    
    if len(daily_occurrences) != num_allowed_days:
        raise ValueError(
            f"Number of daily occurrences ({len(daily_occurrences)}) "
            f"must match number of allowed days ({num_allowed_days})"
        )
    
    return dict(zip(allowed_days, daily_occurrences))


def distribute_occurrences(schedule: Schedule, total_occurrences: int) -> Dict[str, int]:
    """Distribute occurrences across allowed days of the week.
    
    Creates a distribution plan for card occurrences across the allowed days.
    If total_occurrences exceeds the number of allowed days, all days will
    get at least one occurrence and the remainder will be randomly
    distributed among the allowed days.
    
    Args:
        schedule: Schedule object containing allowed days configuration
        total_occurrences: Total number of times the card should appear
                         across the week
                         
    Returns:
        Dictionary with day abbreviations as keys (e.g., 'Mon', 'Tue')
        and number of occurrences as values
        
    Example:
        # For a schedule allowing Mon,Wed,Fri with 5 occurrences
        distribute_occurrences(schedule, 5)
        # Might return: {'Mon': 2, 'Wed': 2, 'Fri': 1}
    """
    # Get list of allowed days from schedule
    allowed_days = schedule.allowed_days.split(',')
    num_allowed_days = len(allowed_days)
    
    # Initialize result dictionary with zeros
    distribution = {day: 0 for day in allowed_days}
    
    # If occurrences <= allowed days, randomly distribute one per day
    if total_occurrences <= num_allowed_days:
        # Randomly select days to get occurrences
        selected_days = random.sample(allowed_days, total_occurrences)
        for day in selected_days:
            distribution[day] = 1
        return distribution
        
    # If occurrences > allowed days:
    # 1. First give one occurrence to each day
    for day in allowed_days:
        distribution[day] = 1
        
    # 2. Randomly distribute the remaining occurrences
    remaining = total_occurrences - num_allowed_days
    for _ in range(remaining):
        # Randomly select a day to increment
        day = random.choice(allowed_days)
        distribution[day] += 1
        
    return distribution


def distribute_fixed_daily_occurrences(schedule: Schedule, times_per_day: int) -> Dict[str, int]:
    """Create a distribution of fixed occurrences per allowed day.
    
    Each allowed day in the schedule receives exactly the same number of occurrences.
    This ensures consistent daily review frequency across the week.
    
    Args:
        schedule: Schedule object containing allowed days configuration
        times_per_day: Number of times to schedule per allowed day
                      
    Returns:
        Dictionary mapping day abbreviations (e.g., 'Mon', 'Tue') to
        the number of occurrences for that day
        
    Example:
        # For a schedule allowing Mon,Wed,Fri with 2 occurrences per day
        distribute_fixed_daily_occurrences(schedule, 2)
        # Returns: {'Mon': 2, 'Wed': 2, 'Fri': 2}
    """
    # Get list of allowed days from schedule
    allowed_days = schedule.allowed_days.split(',')
    
    # Initialize result dictionary assigning times_per_day to each allowed day
    distribution = {day: times_per_day for day in allowed_days}
    
    return distribution


def select_weighted_cards(cards: List[FlashCard], count: int) -> List[FlashCard]:
    """Select flash cards based on their calculated weights.
    
    Uses weighted random selection where each card's probability of being
    selected is proportional to its calculated weight. This ensures that
    cards with higher weights (from category priority and difficulty)
    are more likely to be selected while still maintaining randomness.
    
    If count exceeds the number of available cards, cards will be repeated
    to reach the desired count, with selection probability still based on weights.
    
    Args:
        cards: List of available FlashCard objects to select from
        count: Number of cards to select. Cards may be repeated if count
               exceeds the number of available cards.
    
    Returns:
        List of selected FlashCard objects, may contain repeats if
        count > len(cards)
    
    Example:
        # Get 5 cards weighted by priority/difficulty (may repeat cards)
        selected = select_weighted_cards(available_cards, 5)
    """
    if not cards:
        return []
    
    # Calculate weights for all cards
    weights = [card.calculate_weight() for card in cards]
    total_weight = sum(weights)
    
    # Normalize weights to probabilities
    probabilities = [w/total_weight for w in weights]
    
    # Select cards using weighted choice with replacement
    indices = list(range(len(cards)))
    selected_indices = random.choices(
        population=indices,
        weights=probabilities,
        k=count
    )
    
    # Return selected cards (may include repeats)
    return [cards[i] for i in selected_indices]


def create_scheduled_event(
    session: Session,
    schedule: Schedule,
    flash_card: FlashCard,
    target_date: Optional[datetime.date] = None
) -> Optional[ScheduledEvent]:
    """Create a scheduled event based on schedule constraints.
    
    Generates an appropriate datetime for the event considering the schedule's:
    - Allowed days
    - Time window (start_hour to end_hour)
    - Frequency mode settings
    - Existing events (avoiding conflicts)
    
    Args:
        session: Database session
        schedule: Schedule object containing constraints
        flash_card: FlashCard to be scheduled
        target_date: Optional specific date to schedule for.
            If None, uses today's date.
            
    Returns:
        Created ScheduledEvent if successful, None if no valid time slot found
        
    Example:
        event = create_scheduled_event(session, schedule, card)
        if event:
            session.add(event)
            session.commit()
    """
    # Use target date or today
    target_date = target_date or datetime.date.today()
    
    # Parse allowed days from schedule
    allowed_days = set(schedule.allowed_days.split(','))
    
    # If target date is not allowed, return None
    if target_date.strftime('%a') not in allowed_days:
        return None
        
    minutes_in_window = calculate_minutes_in_schedule_window(schedule)
    
    # Try different times based on frequency mode
    if schedule.frequency_mode == FrequencyMode.FIXED_INTERVAL:
        if schedule.interval_minutes is None:
            return None
        interval = schedule.interval_minutes
    else:
        # For other modes, try every 15 minutes
        interval = 15
    
    # Calculate number of attempts
    attempts = minutes_in_window // interval
    
    # Randomly select a starting hour within the allowed window
    random_hour = random.randint(schedule.start_hour, schedule.end_hour - 1)
    base_time = datetime.datetime.combine(
        target_date,
        datetime.time(hour=random_hour)
    )
    
    # Try different time slots
    for i in range(attempts):
        proposed_time = base_time + datetime.timedelta(minutes=i * interval)
        
        # Check if this time slot is available
        if ScheduledEvent.is_time_slot_available(session, proposed_time):
            # Create and return the event
            event = ScheduledEvent(
                schedule_uuid=schedule.uuid,
                flash_card_uuid=flash_card.uuid,
                scheduled_datetime=proposed_time,
                status=EventStatus.PENDING
            )
            return event
            
    # No suitable time slot found
    return None


def get_days_until(from_date: datetime.date, day_name: str) -> int:
    """Calculate days until next occurrence of a day of the week.
    
    Args:
        from_date: Starting date
        day_name: Three letter day name (e.g., 'Mon', 'Tue')
        
    Returns:
        Number of days until next occurrence (0-6)
    """
    # Convert three-letter day to weekday number (0=Monday, 6=Sunday)
    target_day = {
        'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3,
        'Fri': 4, 'Sat': 5, 'Sun': 6
    }[day_name]
    
    current_day = from_date.weekday()
    days_ahead = target_day - current_day
    
    if days_ahead <= 0:  # Target day has already occurred this week
        days_ahead += 7  # Wait for next week
        
    return days_ahead


def _schedule_fixed_interval_event(
    session: 'Session',
    schedule: 'Schedule',
    card: 'FlashCard',
    target_date: datetime.date,
    minutes_in_window: int,
) -> Optional['ScheduledEvent']:
    """
    Attempts to schedule one event using the FIXED_INTERVAL mode.
    
    Returns the created ScheduledEvent or None if no slot is found.
    """
    base_time = datetime.datetime.combine(
        target_date,
        datetime.time(hour=schedule.start_hour)
    )
    # Start the search from a random minute (5-25) as per the original logic
    current_minute = random.randint(5, 25) 
    
    while current_minute < minutes_in_window:
        proposed_time = base_time + datetime.timedelta(minutes=current_minute)
        
        if ScheduledEvent.is_time_slot_available(session, proposed_time):
            # Slot found, create the event
            return ScheduledEvent(
                schedule_uuid=schedule.uuid,
                flash_card_uuid=card.uuid,
                scheduled_datetime=proposed_time,
                status=EventStatus.PENDING
            )
        
        # Advance the minute by the fixed interval
        if schedule.interval_minutes is not None:
            current_minute += schedule.interval_minutes
        else:
            # Avoid infinite loop if interval_minutes is None
            break 
            
    return None

def _schedule_random_time_event(
    session: 'Session',
    schedule: 'Schedule',
    card: 'FlashCard',
    target_date: datetime.date,
    minutes_in_window: int,
) -> Optional['ScheduledEvent']:
    """
    Attempts to schedule one event using the TIMES_PER_DAY / TIMES_PER_WEEK mode (random time).
    
    Returns the created ScheduledEvent or None if no slot is found after 3 attempts.
    """

    for _ in range(3): # Try up to 3 times
        random_minute = random.randint(0, minutes_in_window - 1)

        proposed_time = datetime.datetime.combine(
            target_date,
            datetime.time(hour=schedule.start_hour)
        ) + datetime.timedelta(minutes=random_minute)

        if ScheduledEvent.is_time_slot_available(session, proposed_time):
            # Slot found, create the event
            return ScheduledEvent(
                schedule_uuid=schedule.uuid,
                flash_card_uuid=card.uuid,
                scheduled_datetime=proposed_time,
                status=EventStatus.PENDING
            )

    return None


def schedule_events_for_day(
    session: Session,
    schedule: Schedule,
    cards_to_schedule: List[FlashCard],
    target_date: datetime.date,
    minutes_in_window: int,
) -> Tuple[List[ScheduledEvent], int]:
    """
    Schedules all events for a specific list of FlashCards on a given date.

    Args:
        session: DB session for checking availability.
        schedule: Schedule object with timing constraints.
        cards_to_schedule: The exact list of FlashCards to schedule on this day.
        target_date: The specific date for which to schedule the events.
        minutes_in_window: Total available minutes in the time window.
        
    Returns:
        A tuple containing: 
        1. A list of created ScheduledEvent objects (New list created inside).
        2. The number of events successfully created (int).
    """
    if not cards_to_schedule:
        return [], 0
            
    events_created_for_day: List[ScheduledEvent] = []
    events_created_count = 0
    
    if schedule.frequency_mode == FrequencyMode.FIXED_INTERVAL:
        scheduler_func = _schedule_fixed_interval_event
    else: # TIMES_PER_DAY / TIMES_PER_WEEK
        scheduler_func = _schedule_random_time_event
    
    for card in cards_to_schedule:
        # Call the chosen strategy to try and schedule the event
        new_event = scheduler_func(
            session=session,
            schedule=schedule,
            card=card,
            target_date=target_date,
            minutes_in_window=minutes_in_window
        )
        
        if new_event:
            # Event was successfully created
            events_created_for_day.append(new_event)
            session.add(new_event)
            events_created_count += 1
        else:
            # If the card couldn't be scheduled (no time slot found), 
            # stop trying for the rest of the cards for this day.
            break
            
    return events_created_for_day, events_created_count


def get_next_occurrence_dates(distribution: Dict[str, int]) -> Dict[str, datetime.date]:
    """
    Calculates the specific datetime.date for the next occurrence of each day
    specified in the distribution keys, starting from today.
    
    Args:
        distribution: A dictionary mapping day names (e.g., 'Mon', 'Wed') 
        to an integer count (the count value is not used for date calculation).
                      
    Returns:
        A dictionary mapping the day names to their next datetime.date object.
    """
    today = datetime.date.today()
    day_dates = {}
    
    for day_name in distribution.keys():
        # Encuentra cuántos días faltan para la próxima ocurrencia
        days_ahead = get_days_until(today, day_name)
        
        # Calcula la fecha real
        day_dates[day_name] = today + datetime.timedelta(days=days_ahead)
        
    return day_dates


def schedule_events_from_distribution(
    session: Session,
    schedule: Schedule,
    flash_cards: List[FlashCard],
    distribution: Dict[str, int]
) -> List[ScheduledEvent]:
    """Schedule events for flash cards based on day distribution.
    
    For each day in the distribution, schedules the specified number of events,
    properly spacing them according to the schedule's frequency mode.
    
    Args:
        session: Database session for checking time slot availability
        schedule: Schedule object containing timing constraints
        flash_cards: List of FlashCards to schedule (may contain repeats)
        distribution: Dictionary mapping days to number of occurrences
        
    Returns:
        List of created ScheduledEvent objects
        
    Example:
        events = schedule_events_from_distribution(
            session, schedule, cards,
            {'Mon': 2, 'Wed': 1}
        )
    """
    minutes_in_window = calculate_minutes_in_schedule_window(schedule)
    # Keep track of created events
    scheduled_events = []
    # Keep track of current position in flash_cards list
    card_index = 0
    total_cards = len(flash_cards)

    day_dates = get_next_occurrence_dates(distribution)

    for day_name, count in distribution.items():
        if count <= 0:
            continue
            
        # Get the specific target date for this day
        target_date = day_dates[day_name]

        # Determine the sublist of cards needed for this day
        cards_to_schedule: List[FlashCard] = []
        for i in range(count):
            # Use the modulo operator to handle card cycling
            cards_to_schedule.append(flash_cards[(card_index + i) % total_cards])
        
        # Call the simplified helper function
        events_for_day, events_created_count = schedule_events_for_day(
            session=session,
            schedule=schedule,
            cards_to_schedule=cards_to_schedule,
            target_date=target_date, # Send the specific date
            minutes_in_window=minutes_in_window,
        )
        
        # EXPAND the main list with the events returned by the helper
        scheduled_events.extend(events_for_day)
        
        # Advance the card_index by the number of events *actually* created.
        card_index = (card_index + events_created_count) % total_cards
                        
    return scheduled_events


def calculate_total_events_and_daily_counts(
    schedule: Schedule
) -> Tuple[int, Optional[List[int]]]:
    """
    Calculates the total number of events required for a schedule and the daily 
    counts for TIMES_PER_DAY mode.

    Args:
        schedule: Schedule object containing frequency configuration.
        
    Returns:
        Tuple containing:
        - The total number of events (amount_of_events).
        - A list of daily counts (List[int]) if frequency mode is TIMES_PER_DAY 
          with a range, or None otherwise.
          
    Raises:
        ValueError: If required schedule fields are missing for the mode.
    """
    allowed_days = schedule.allowed_days.split(',')
    num_allowed_days = len(allowed_days)
    amount_of_events: int = 0
    times_per_days: Optional[List[int]] = None
    
    if schedule.frequency_mode == FrequencyMode.TIMES_PER_WEEK:
        if schedule.times_per_week is None:
            raise ValueError("Times per week schedule must have times_per_week set")
        amount_of_events = schedule.times_per_week
        
    elif schedule.frequency_mode == FrequencyMode.TIMES_PER_DAY:
        if schedule.min_times_per_day is None or schedule.max_times_per_day is None:
            raise ValueError("Times Per Day schedule must have min_times_per_day and max_times_per_day set")
        
        min_times = schedule.min_times_per_day
        max_times = schedule.max_times_per_day

        if min_times == max_times:
            # Conteo fijo por día
            times_per_day_fixed = min_times
            amount_of_events = times_per_day_fixed * num_allowed_days
        else:
            # Conteo aleatorio por día
            times_per_days = [random.randint(min_times, max_times) for _ in allowed_days]
            amount_of_events = sum(times_per_days)
            
    elif schedule.frequency_mode == FrequencyMode.FIXED_INTERVAL:
        if schedule.interval_minutes is None:
            raise ValueError("Fixed interval schedule must have interval_minutes set")
        
        minutes_in_window = calculate_minutes_in_schedule_window(schedule)
        
        # Calcula cuántos eventos caben en un día
        events_per_day = minutes_in_window // schedule.interval_minutes
        amount_of_events = events_per_day * num_allowed_days

    else:
        # Esto maneja un modo de frecuencia no reconocido, si lo hubiera
        raise ValueError(f"Unknown frequency mode: {schedule.frequency_mode}")

    # Retorna el conteo total y los conteos diarios (si aplica)
    return amount_of_events, times_per_days


def determine_weekly_event_distribution(
    schedule: 'Schedule',
    amount_of_events: int,
    times_per_days: Any, # int or List[int], depending on the mode
) -> Dict[str, int]:
    """
    Determines the final event distribution (day -> count) based on the schedule's frequency mode.

    Args:
        schedule: Schedule object containing frequency_mode and allowed_days.
        amount_of_events: Total number of events calculated for the period.
        times_per_days: The daily counts, used specifically for TIMES_PER_DAY mode.

    Returns:
        A dictionary mapping day names (str) to the number of events (int) scheduled for that day.
    """
    allowed_days = schedule.allowed_days.split(',')
    num_allowed_days = len(allowed_days)
    distribution: Dict[str, int] = {}

    if schedule.frequency_mode == FrequencyMode.TIMES_PER_WEEK:
        distribution = distribute_occurrences(schedule, amount_of_events)

    elif schedule.frequency_mode == FrequencyMode.TIMES_PER_DAY:
        if isinstance(times_per_days, list):
            # If times_per_days is a list, use the ordered/specific distribution.
            distribution = distribute_ordered_occurrences(schedule, times_per_days)
        else:
            daily_count = amount_of_events // num_allowed_days
            distribution = distribute_fixed_daily_occurrences(schedule, daily_count)

    else:  # FrequencyMode.FIXED_INTERVAL
        daily_count = amount_of_events // num_allowed_days
        distribution = distribute_fixed_daily_occurrences(schedule, daily_count)

    return distribution


def generate_schedule_events(
    session: Session,
    schedule: Schedule
) -> List[FlashCard]:
    """
    Generates scheduled events for a given schedule.

    This function handles:
    1. Getting relevant flash cards based on schedule scope
    2. Calculating total events needed based on frequency mode
    3. Selecting weighted cards for scheduling
    4. Distributing events across allowed days

    Args:
        session: Database session for queries
        schedule: Schedule object containing configuration

    Returns:
        Tuple containing:
        - List of selected FlashCards to schedule (may include repeats)

    Example:
        cards, distribution = prepare_schedule_distribution(session, schedule)
        # cards: [card1, card2, card1] (repeats possible)
        # distribution: {'Mon': 2, 'Wed': 1} (example distribution)
    """
    # Get relevant flash cards based on scope
    cards = []
    category_uuid = None
    if schedule.scope == Scope.CATEGORY:
        category_uuid = schedule.category_uuid
    if schedule.scope == Scope.CARD:
        cards = [session.get(FlashCard, schedule.flash_card_uuid)]
    else: # CATEGORY ALL
        cards = get_flash_cards(session, category_uuid)
    
    times_per_days = None

    amount_of_events, times_per_days = calculate_total_events_and_daily_counts(schedule)

    if not cards:
        logger.warning("There are no Flash Cards available for scheduling.")
        return []
    # Filter out any None values and convert to List[FlashCard]
    valid_cards = [card for card in cards if card is not None]
    if not valid_cards:
        logger.warning("No valid Flash Cards found for scheduling.")
        return []
    selected_cards = select_weighted_cards(valid_cards, amount_of_events)

    distribution = determine_weekly_event_distribution(
        schedule, amount_of_events, times_per_days)

    schedule_events_from_distribution(session, schedule, selected_cards, distribution)

    return selected_cards


def generate_events_from_schedules(
    session: 'Session'
) -> int:
    """
    Retrieves all active schedules and calls generate_schedule_events for each one.
    This function acts as the main orchestrator for the entire scheduling process.

    Args:
        session: Database session for queries and updates.

    Returns:
        The total count of FlashCards (or events) that were processed/scheduled 
        across all schedules.
    """
    all_schedules = session.scalars(select(Schedule).where(Schedule.active == True)).all()
    total_cards_processed = 0
    
    if not all_schedules:
        return 0 

    for schedule in all_schedules:
        processed_cards = generate_schedule_events(session, schedule)
        total_cards_processed += len(processed_cards)

    return total_cards_processed
