#!/usr/bin/env python3

import argparse
import ldclient
from ldclient import Context
from ldclient.config import Config
from faker import Faker
from faker.providers import DynamicProvider
import time
import random
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logging(log_file='simulator.log'):
    """Configure logging with rotation"""
    logger = logging.getLogger('LaunchDarklySimulator')
    logger.setLevel(logging.INFO)
    
    # Create rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger

def initialize_launchdarkly(sdk_key):
    """Initialize LaunchDarkly client"""
    config = Config(sdk_key=sdk_key, http=ldclient.config.HTTPConfig(connect_timeout=5))
    ldclient.set_config(config)
    return ldclient.get()

def setup_faker():
    """Setup Faker with custom providers"""
    fake = Faker()
    
    # Define custom providers using DynamicProvider
    brands_provider = DynamicProvider(
        provider_name="brand",
        elements=["Admiral", "Diamond", "Elephant", "Toothbrush", "Biscuit"]
    )
    
    price_provider = DynamicProvider(
        provider_name="price",
        elements=[93.84, 143.73, 101.35, 86.02, 46.91, 125.62, 77.85, 99.68, 73.99, 148.79]
    )
    
    product_provider = DynamicProvider(
        provider_name="product",
        elements=["Car", "Home", "Motorcycle", "Renters"]
    )
    
    tier_provider = DynamicProvider(
        provider_name="tier",
        elements=["Bronze", "Silver", "Gold", "Platinum"]
    )
    
    fake.add_provider(brands_provider)
    fake.add_provider(price_provider)
    fake.add_provider(product_provider)
    fake.add_provider(tier_provider)
    
    return fake

def generate_user_data(fake):
    """Generate fake user data"""
    return {
        'user_id': fake.uuid4(),
        'brand': fake.brand(),
        'price': fake.price(),
        'product': fake.product(),
        'tier': fake.tier()
    }

def get_tracking_probability(user_data, base_prob, target_attribute=None, target_value=None, boost_factor=1.5):
    """Determine tracking probability based on user attributes"""
    if target_attribute and target_value:
        # Convert both to lowercase for case-insensitive comparison
        if target_attribute.lower() in ['brand', 'product', 'tier'] and \
           user_data[target_attribute.lower()].lower() == target_value.lower():
            return min(1.0, base_prob * boost_factor)
        # Handle price separately as it's numeric
        elif target_attribute.lower() == 'price' and \
             abs(float(user_data['price']) - float(target_value)) < 0.01:
            return min(1.0, base_prob * boost_factor)
    return base_prob

def simulate_traffic(client, fake, num_records, control_prob, treatment_prob, delay, logger, target_attribute=None, target_value=None):
    """Simulate user traffic with LaunchDarkly flag evaluation"""
    for i in range(num_records):
        try:
            user_data = generate_user_data(fake)
            
            user_context = Context.builder(user_data['user_id']) \
                .kind("user") \
                .set("brand", user_data['brand']) \
                .set("product", user_data['product']) \
                .set("tier", user_data['tier']) \
                .build()

            # Evaluate flag
            variation_detail = client.variation_detail(
                "show-sponsored-product", 
                user_context, 
                'false'
            )

            base_prob = treatment_prob if variation_detail.value else control_prob
            actual_prob = get_tracking_probability(
                user_data, 
                base_prob, 
                target_attribute, 
                target_value
            )

            if random.random() < actual_prob:
                client.track("in-cart-total-price", user_context, metric_value=user_data['price'])
                client.track("customer-checkout", user_context)
                logger.info(
                    f"Tracked event for user {user_data['user_id']} - "
                    f"Brand: {user_data['brand']}, Product: {user_data['product']}, "
                    f"Tier: {user_data['tier']}, Price: {user_data['price']} "
                    f"(Probability: {actual_prob:.2f})"
                )

            time.sleep(delay)
            
            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1} records")

        except Exception as e:
            logger.error(f"Error processing record {i}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='LaunchDarkly Traffic Simulator')
    parser.add_argument('--sdk-key', required=True, help='LaunchDarkly SDK key')
    parser.add_argument('--num-records', type=int, default=100, help='Number of records to generate')
    parser.add_argument('--control-prob', type=float, default=0.3, help='Control probability')
    parser.add_argument('--treatment-prob', type=float, default=0.35, help='Treatment probability')
    parser.add_argument('--delay', type=float, default=0.05, help='Delay between records in seconds')
    parser.add_argument('--log-file', default='simulator.log', help='Log file path')
    parser.add_argument('--target-attribute', choices=['brand', 'product', 'price', 'tier'], 
                        help='Target attribute to boost probability for')
    parser.add_argument('--target-value', help='Target value for the specified attribute')

    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_file)
    logger.info("Starting LaunchDarkly Traffic Simulator")

    if bool(args.target_attribute) != bool(args.target_value):
        logger.error("Both target-attribute and target-value must be provided together")
        sys.exit(1)

    try:
        # Initialize LaunchDarkly
        client = initialize_launchdarkly(args.sdk_key)
        if not client.is_initialized():
            logger.error("LaunchDarkly client failed to initialize")
            sys.exit(1)

        # Setup Faker
        fake = setup_faker()

        # Run simulation
        simulate_traffic(
            client=client,
            fake=fake,
            num_records=args.num_records,
            control_prob=args.control_prob,
            treatment_prob=args.treatment_prob,
            delay=args.delay,
            logger=logger,
            target_attribute=args.target_attribute,
            target_value=args.target_value
        )

        logger.info("Simulation completed successfully")

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
