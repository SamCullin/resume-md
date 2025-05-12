{
  description = "UV development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        dirName = builtins.baseNameOf ./.;
      in
      {
        devShells = {
          default = pkgs.mkShell {
            packages = with pkgs; [
              uv
            ];

            shellHook = ''
              # Create and activate virtual environment if it doesn't exist
              if [ ! -d .venv ]; then
                uv python -m venv .venv
              fi
              source .venv/bin/activate

              uv sync
              
            '';
          };
        };
      });
}
