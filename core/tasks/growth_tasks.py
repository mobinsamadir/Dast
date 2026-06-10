import logging
from celery import shared_task
from django.db import transaction
from django.db.models import F

from games.models import GameRoom
from accounts.models import Referral
from core.models import SiteConfig

logger = logging.getLogger(__name__)

@shared_task
def process_referral_commissions():
    config = SiteConfig.load()
    commission_rate = config.commission_rate
    
    # Process only finished games that haven't been processed yet
    games_to_process = GameRoom.objects.filter(status='FINISHED', commission_processed=False).prefetch_related('players__referral_info')
    
    games_processed_count = 0
    total_commission_added = 0
    
    with transaction.atomic():
        for game in games_to_process:
            # The house edge logic might be custom depending on the game type
            # We assume a standard simple calculation: (entry_fee * capacity) - reward_pool
            # or entry_fee itself if reward_pool doesn't represent payout
            # However, typically house_edge = (entry_fee * capacity) - reward_pool
            total_entry = game.entry_fee * game.capacity
            house_edge = total_entry - game.reward_pool
            
            # If house edge is 0 or negative, skip
            if house_edge <= 0:
                game.commission_processed = True
                game.save(update_fields=['commission_processed'])
                continue
                
            commission_amount = int(house_edge * commission_rate)
            
            if commission_amount <= 0:
                game.commission_processed = True
                game.save(update_fields=['commission_processed'])
                continue

            for player in game.players.all():
                # Add to total spent coins
                player.total_spent_coins += game.entry_fee
                player.save(update_fields=['total_spent_coins'])
                
                if hasattr(player, 'referral_info') and player.referral_info:
                    referral = player.referral_info
                    referrer = referral.referrer
                    
                    # Anti-Fraud Check
                    max_allowed_commission = int(referrer.total_spent_coins * 0.20)
                    current_generated = referral.commission_generated
                    
                    # How much room is left for this referrer?
                    room_left = max_allowed_commission - current_generated
                    
                    if room_left > 0:
                        actual_commission = min(commission_amount, room_left)
                        
                        referral.commission_generated += actual_commission
                        referral.save(update_fields=['commission_generated'])
                        
                        referrer.unclaimed_commission += actual_commission
                        referrer.save(update_fields=['unclaimed_commission'])
                        
                        total_commission_added += actual_commission

            game.commission_processed = True
            game.save(update_fields=['commission_processed'])
            games_processed_count += 1
            
    logger.info(f"Processed {games_processed_count} games. Added {total_commission_added} in commissions.")
    return f"Processed {games_processed_count} games, {total_commission_added} total commission."

