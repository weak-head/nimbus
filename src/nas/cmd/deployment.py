"""
Provides functionality related to managing deployments.
The following commands are available:
  - up
  - down
"""

from __future__ import annotations

from abc import ABC
from pathlib import Path

from nas.core.runner import Runner
from nas.utils.log import Log


class Deployment(ABC):
    """
    Base class for deployment related commands.

    Before running any specific commands, it:
        - discovers services defined on the file system
        - maps requested services
    """

    def __init__(self, commands: list[Command], section: str, root_folder: str, runner: Runner, log: Log):
        """
        Creates a new instance of `Deployment`.

        :param commands: Default set of commands to execute.
        :param section: Default command section.
        :param root_folder: Root folder with services.
        :param runner: Command runner.
        :param log: Application log writer.
        """
        self._commands = commands
        self._section = section
        self._root_folder = root_folder
        self._runner = runner
        self._log = log

    def execute(self, services: list[str]) -> None:
        """
        Execute the command for all specified services.

        :param services: The list of services to execute the command for.
        """

        # Informational section with the general
        # overview of the command chain execution plan.
        self._log_info(services)

        # Try to map the requested services
        # to the set of services that exist on the file system.
        service_mapping = self._map_services(services)
        self._log_services(service_mapping)

        # If nothing has been mapped, there is no reason to continue
        if not service_mapping.successful:
            return

        # Execute the main chain of commands
        # on each mapped service.
        self._execute(service_mapping.mapped)

    def _log_info(self, services: list[str]):
        """
        Write to log 'Information' section.

        :param services: List of requested services.
        """
        log = self._log.section("Information:")
        log.out("root folder:", self._root_folder)

        if not services:
            log.out("services:", "*")
        else:
            log.section("services:").multiline(services, as_list=True)

        log.out()

    def _log_services(self, service_mapping: ServiceMapping):
        """
        Write to log 'Services' section.

        :param service_mapping: Service mapping information.
        """
        log = self._log.section("Services:")
        log.out("status:", service_mapping.status)
        log.out("mapped services:", len(service_mapping.mapped))
        log.out("unmapped services:", len(service_mapping.unmapped))

        log_mapping = log.section("mapping:")
        for srv in service_mapping.services:
            log_mapping.out(srv.name, "-> " + (srv.folder if srv.is_mapped else "[Not Mapped]"))
        log_mapping.out()

    def _map_services(self, services: list[str]) -> ServiceMapping:
        """
        Maps the requested services to the set of services
        that exist on the local file system.

        :param services: The list of service names to discover and map.
        :return: The service mapping result.
        """

        srv_map = ServiceMapping([])

        # The convention of the service mapping,
        # is that each sub-directory under the root folder
        # is a single service with a docker-compose.yml file and
        # a required environment configuration.
        service_folders = self._discover_candidates(self._root_folder)

        # If no services are explicitly specified,
        # it means that the operation should be executed
        # for all services that could be discovered.
        if not services:
            for folder in service_folders:
                mapping = Service(folder.split("/")[-1])
                mapping.folder = folder
                mapping.is_mapped = True
                srv_map.services.append(mapping)

        # Map each requested service to a service,
        # that has been discovered under the root folder.
        else:
            for name in services:
                mapping = Service(name)
                srv_map.services.append(mapping)

                for folder in service_folders:
                    if folder.split("/")[-1] == name:
                        mapping.folder = folder
                        mapping.is_mapped = True
                        break

        srv_map.services.sort(key=lambda srv: (not srv.is_mapped, srv.name))
        return srv_map

    def _discover_candidates(self, root_folder: str) -> list[str]:
        """
        Discover all potential service candidates under
        the specified file system path.

        :param root_folder: Path to directory with services.
        :return: List of sub-folders, with potential `Service` candidates.
        """
        folder_path = Path(root_folder)
        return [f.as_posix() for f in folder_path.iterdir() if f.is_dir()]

    def _execute(self, services: list[Service]) -> None:
        """
        Execute a default `self._cmd` for all provided services.
        In case if the provided `Service` is not mapped,
        the default `self._cmd` would not be executed for this service,
        and the error would be reported.

        :param services: The list of `Services` to execute the commands for.
        """

        log = self._log.section(self._section)
        for service_ix, service in enumerate(services):
            log_srv = log.section(f"{service.name} [{service_ix+1}/{len(services)}]")

            # Skip services that are not mapped
            if not service.is_mapped:
                log_srv.out("status:", "failed (not mapped)")
                log_srv.out()
                continue

            for command_ix, command in enumerate(self._commands):
                log_cmd = log_srv.section(f"[{command_ix+1}/{len(self._commands)}] $> {command.cmd}")

                # Execute the command and write to log
                # the result of command execution.
                proc = self._runner.execute(command.cmd, service.folder)
                log_cmd.process(proc, cmd=False)

                # Do not continue the command chain execution,
                # if this command has failed.
                if not proc.successful:
                    break

            log_srv.out()


class Up(Deployment):
    """Deploy services command."""

    def __init__(self, root_folder: str, runner: Runner, log: Log):
        """Create a new instance of `Up` command."""
        super().__init__(
            [
                Command("ls -la"),
                Command("docker compose config --quiet"),
                Command("docker compose pull"),
                Command("docker compose down"),
                Command("docker compose up --detach"),
                Command("docker compose top"),
            ],
            "Deploy:",
            root_folder,
            runner,
            log,
        )


class Down(Deployment):
    """Undeploy services command."""

    def __init__(self, root_folder: str, runner: Runner, log: Log):
        """Create a new instance of 'Down' command."""
        super().__init__(
            [
                Command("ls -la"),
                Command("docker compose down"),
            ],
            "Undeploy:",
            root_folder,
            runner,
            log,
        )


class ServiceMapping:
    """Result of mapping a services to the deployment configuration."""

    def __init__(self, services: list[Service]):
        """
        Create a new instance of `ServiceMapping`.

        :param services: The list of services.
        """

        self.services = services
        """The list of services."""

    @property
    def status(self) -> str:
        """Overall status of the service mapping."""
        return "success" if self.successful else "failed"

    @property
    def successful(self) -> bool:
        """Return True, if the service mapping is successful."""
        return len(self.mapped) > 0

    @property
    def mapped(self) -> list[Service]:
        """List of services that were mapped successfully."""
        return [srv for srv in self.services if srv.is_mapped]

    @property
    def unmapped(self) -> list[Service]:
        """List of services that were not mapped."""
        return [srv for srv in self.services if not srv.is_mapped]


class Service:
    """Service is a smallest deployable unit of execution."""

    def __init__(self, name: str):
        """
        Creates a new instance of `Service`,
        with default values initialized.

        :param name: Service name.
        """

        self.name = name
        """Service name."""

        self.folder = None
        """A folder with service deployment configuration."""

        self.is_mapped = False
        """`True` if the service is mapped and `self.folder` is valid."""


class Command:
    """A single command to execute."""

    def __init__(self, cmd: str):
        """
        Creates a new instance of `Command`.

        :param cmd: A single command to execute.
        """

        self.cmd = cmd
        """A single command to execute."""
