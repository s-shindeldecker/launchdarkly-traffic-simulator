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
    
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
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
    
    user_type_provider = DynamicProvider(
        provider_name="user_type",
        elements=["new", "returning", "premium", "basic"]
    )
    
    region_provider = DynamicProvider(
        provider_name="region",
        elements=["north", "south", "east", "west"]
    )
    
    fake.add_provider(user_type_provider)
    fake.add_provider(region_provider)
    
    return fake

def generate_user_data(fake):
    """Generate fake user data"""
    return {
        'user_id': fake.uuid4(),
        'user_type': fake.user_type(),
        'region': fake.region(),
        'age': random.randint(18, 80)
    }

def get_tracking_probability(user_data, base_prob, target_attribute=None, target_value=None, boost_factor=1.5):
    """Determine tracking probability based on user attributes"""
    if target_attribute and target_value:
        if str(user_data.get(target_attribute, '')).lower() == str(target_value).lower():
            return min(1.0, base_prob * boost_factor)
    return base_prob

def simulate_traffic(client, feature_flag_key, fake, num_records, control_prob, treatment_prob, 
                    delay, logger, target_attribute=None, target_value=None, 
                    enable_tracking=True, metric_name=None):
    """Simulate user traffic with LaunchDarkly flag evaluation"""
    default_metric_name = f"flag-{feature_flag_key}-evaluation"
    actual_metric_name = metric_name if metric_name else default_metric_name

    for i in range(num_records):
        try:
            user_data = generate_user_data(fake)
            
            # Create user context with generated data
            user_context = Context.builder(user_data['user_id']) \
                .kind("user") \
                .set("userType", user_data['user_type']) \
                .set("region", user_data['region']) \
                .set("age", user_data['age']) \
                .build()

            # Evaluate feature flag
            variation_detail = client.variation_detail(
                feature_flag_key,
                user_context, 
                False
            )

            # Determine tracking probability
            base_prob = treatment_prob if variation_detail.value else control_prob
            actual_prob = get_tracking_probability(
                user_data, 
                base_prob, 
                target_attribute, 
                target_value
            )

            # Track event if enabled and probability threshold is met
            if enable_tracking and random.random() < actual_prob:
                client.track(actual_metric_name, user_context)
                
                logger.info(
                    f"Tracked event '{actual_metric_name}' for user {user_data['user_id']} - "
                    f"Type: {user_data['user_type']}, Region: {user_data['region']}, "
                    f"Age: {user_data['age']} "
                    f"(Flag Value: {variation_detail.value}, Probability: {actual_prob:.2f})"
                )
            else:
                logger.info(
                    f"Evaluated flag '{feature_flag_key}' for user {user_data['user_id']} - "
                    f"Type: {user_data['user_type']}, Region: {user_data['region']}, "
                    f"Age: {user_data['age']} "
                    f"(Flag Value: {variation_detail.value}, Tracking: {'Disabled' if not enable_tracking else 'Not Selected'})"
                )

            time.sleep(delay)
            
            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1} records")

        except Exception as e:
            logger.error(f"Error processing record {i}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='LaunchDarkly Traffic Simulator')
    parser.add_argument('--sdk-key', required=True, help='LaunchDarkly SDK key')
    parser.add_argument('--feature-flag', required=True, help='Feature flag key to evaluate')
    parser.add_argument('--num-records', type=int, default=100, help='Number of records to generate')
    parser.add_argument('--control-prob', type=float, default=0.3, help='Control probability')
    parser.add_argument('--treatment-prob', type=float, default=0.35, help='Treatment probability')
    parser.add_argument('--delay', type=float, default=0.05, help='Delay between records in seconds')
    parser.add_argument('--log-file', default='simulator.log', help='Log file path')
    parser.add_argument('--target-attribute', choices=['user_type', 'region', 'age'], 
                        help='Target attribute to boost probability for')
    parser.add_argument('--target-value', help='Target value for the specified attribute')
    parser.add_argument('--enable-tracking', action='store_true', help='Enable event tracking')
    parser.add_argument('--metric-name', help='Custom metric name for tracking events')

    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_file)
    logger.info("Starting LaunchDarkly Traffic Simulator")
    logger.info(f"Event tracking is {'enabled' if args.enable_tracking else 'disabled'}")
    if args.enable_tracking and args.metric_name:
        logger.info(f"Using custom metric name: {args.metric_name}")

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
            feature_flag_key=args.feature_flag,
            fake=fake,
            num_records=args.num_records,
            control_prob=args.control_prob,
            treatment_prob=args.treatment_prob,
            delay=args.delay,
            logger=logger,
            target_attribute=args.target_attribute,
            target_value=args.target_value,
            enable_tracking=args.enable_tracking,
            metric_name=args.metric_name
        )

        logger.info("Simulation completed successfully")

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
