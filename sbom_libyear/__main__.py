import argparse
import logging
import sys
from dataclasses import asdict
from pathlib import Path

from .core import LibyearCalculator
from .reports import JSONReportGenerator, TextReportGenerator
from .utils import ConfigLoader, HttpClient


def setup_logging(verbose: bool, debug: bool):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    parser = argparse.ArgumentParser(
        description='Calculates libyear metrics from SBOM files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my-sbom.json
  %(prog)s my-sbom.json --config config.yaml
  %(prog)s my-sbom.json --max-libyears 50
  %(prog)s my-sbom.json --report-path report.json --format json
  %(prog)s my-sbom.json --output report.txt --max-libyears 35
  %(prog)s my-sbom.json -c artifactory-config.yaml --verbose
"""
    )
    
    parser.add_argument('sbom_file', help='Path to SBOM file')
    parser.add_argument('--config', '-c', help='Path to configuration file (config.yaml)')
    parser.add_argument('--output', '-o', help='Output file for text report')
    parser.add_argument('--format', choices=['text', 'json'], default='text', 
                       help='Output format for stdout (default: text)')
    parser.add_argument('--report-path', help='Path for JSON report')
    parser.add_argument('--max-libyears', type=float, 
                       help='Maximum allowed libyears. If exceeded, exit code 1 is returned')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose logging output')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose, args.debug)
    logger = logging.getLogger(__name__)
    
    config_loader = ConfigLoader(args.config)
    
    http_config = config_loader.get_http_config()
    proxy_config = config_loader.get_proxy_config()
    http_client = HttpClient()
    http_client.configure(
        timeout=http_config.get('timeout', 10),
        user_agent=http_config.get('user_agent', 'sbom-libyear-calculator/1.0'),
        proxies=proxy_config
    )
    
    calculator = LibyearCalculator(config_loader)
    
    try:
        libyear_results = calculator.calculate_from_sbom(args.sbom_file)
        
        if args.format == 'json':
            report_generator = JSONReportGenerator()
        else:
            report_generator = TextReportGenerator()
        
        report_str = report_generator.generate(libyear_results)
        report = report_generator._create_report_data(libyear_results)
        
        if args.report_path:
            with open(args.report_path, 'w', encoding='utf-8') as report_file:
                json_generator = JSONReportGenerator()
                report_file.write(json_generator.generate(libyear_results))
            logger.info(f"JSON report saved: {args.report_path}")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as output_file:
                output_file.write(report_str)
            logger.info(f"Report saved: {args.output}")
        else:
            print(report_str)
        
        if args.max_libyears is not None:
            if report.total_libyear > args.max_libyears:
                logger.error(f"Libyear limit exceeded: {report.total_libyear:.2f} > {args.max_libyears}")
                logger.error("Exitcode: 1")
                return 1
            else:
                logger.info(f"Libyear limit maintained: {report.total_libyear:.2f} <= {args.max_libyears}")
        
        logger.info("Analysis completed successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Failed to analyze SBOM: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())