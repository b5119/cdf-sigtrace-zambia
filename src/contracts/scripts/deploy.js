// Deploy CDFConfirmation to the configured network (Amoy testnet).
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  const CDFConfirmation = await hre.ethers.getContractFactory("CDFConfirmation");
  const contract = await CDFConfirmation.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("CDFConfirmation deployed to:", address);
  console.log("Owner:", await contract.owner());
  console.log("\nSet POLYGON_CONTRACT_ADDRESS=" + address + " in the backend .env");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
