const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CDFConfirmation", function () {
  let contract, owner, monitor, confirmerA, confirmerB, confirmerC, outsider;
  const SUB_ID = ethers.id("submission-uuid-0001"); // keccak256 of off-chain UUID
  const CID = "bafkreiabc123def456";

  beforeEach(async function () {
    [owner, monitor, confirmerA, confirmerB, confirmerC, outsider] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("CDFConfirmation");
    contract = await Factory.deploy();
    await contract.waitForDeployment();
    // Authorize three institutional confirmers
    await contract.addConfirmer(confirmerA.address);
    await contract.addConfirmer(confirmerB.address);
    await contract.addConfirmer(confirmerC.address);
  });

  describe("recording submissions", function () {
    it("records a submission requiring N confirmations", async function () {
      await expect(contract.connect(monitor).recordSubmission(SUB_ID, CID, 2))
        .to.emit(contract, "SubmissionRecorded")
        .withArgs(SUB_ID, CID, 2, monitor.address);
      const [cid, required, count, complete] = await contract.getSubmission(SUB_ID);
      expect(cid).to.equal(CID);
      expect(required).to.equal(2);
      expect(count).to.equal(0);
      expect(complete).to.equal(false);
    });

    it("rejects duplicate submission id", async function () {
      await contract.connect(monitor).recordSubmission(SUB_ID, CID, 2);
      await expect(contract.connect(monitor).recordSubmission(SUB_ID, CID, 2))
        .to.be.revertedWith("CDF: already recorded");
    });

    it("rejects required = 0", async function () {
      await expect(contract.connect(monitor).recordSubmission(SUB_ID, CID, 0))
        .to.be.revertedWith("CDF: required must be > 0");
    });
  });

  describe("multi-party confirmation (the core guarantee)", function () {
    beforeEach(async function () {
      await contract.connect(monitor).recordSubmission(SUB_ID, CID, 2);
    });

    it("N-1 confirmations does NOT complete", async function () {
      await contract.connect(confirmerA).confirm(SUB_ID);
      expect(await contract.isComplete(SUB_ID)).to.equal(false);
      expect(await contract.getConfirmationCount(SUB_ID)).to.equal(1);
    });

    it("Nth distinct confirmation completes", async function () {
      await contract.connect(confirmerA).confirm(SUB_ID);
      await expect(contract.connect(confirmerB).confirm(SUB_ID))
        .to.emit(contract, "SubmissionCompleted")
        .withArgs(SUB_ID, 2);
      expect(await contract.isComplete(SUB_ID)).to.equal(true);
    });

    it("a single party CANNOT complete alone (duplicate confirm rejected)", async function () {
      await contract.connect(confirmerA).confirm(SUB_ID);
      // Same confirmer tries again — must revert, count stays 1, not complete
      await expect(contract.connect(confirmerA).confirm(SUB_ID))
        .to.be.revertedWith("CDF: duplicate confirmation");
      expect(await contract.getConfirmationCount(SUB_ID)).to.equal(1);
      expect(await contract.isComplete(SUB_ID)).to.equal(false);
    });

    it("monitor cannot self-confirm their own submission", async function () {
      // Authorize the monitor, but they still cannot confirm their own submission
      await contract.addConfirmer(monitor.address);
      await expect(contract.connect(monitor).confirm(SUB_ID))
        .to.be.revertedWith("CDF: monitor cannot self-confirm");
    });

    it("rejects confirmation from a non-authorized address", async function () {
      await expect(contract.connect(outsider).confirm(SUB_ID))
        .to.be.revertedWith("CDF: not authorized confirmer");
    });

    it("rejects confirmation of an unknown submission", async function () {
      const unknown = ethers.id("does-not-exist");
      await expect(contract.connect(confirmerA).confirm(unknown))
        .to.be.revertedWith("CDF: unknown submission");
    });

    it("rejects confirmation after completion", async function () {
      await contract.connect(confirmerA).confirm(SUB_ID);
      await contract.connect(confirmerB).confirm(SUB_ID);
      await expect(contract.connect(confirmerC).confirm(SUB_ID))
        .to.be.revertedWith("CDF: already complete");
    });

    it("emits Confirmed with running count", async function () {
      await expect(contract.connect(confirmerA).confirm(SUB_ID))
        .to.emit(contract, "Confirmed")
        .withArgs(SUB_ID, confirmerA.address, 1);
    });
  });

  describe("3-of-3 confirmation", function () {
    it("requires all 3 distinct confirmers", async function () {
      await contract.connect(monitor).recordSubmission(SUB_ID, CID, 3);
      await contract.connect(confirmerA).confirm(SUB_ID);
      await contract.connect(confirmerB).confirm(SUB_ID);
      expect(await contract.isComplete(SUB_ID)).to.equal(false); // 2 of 3
      await contract.connect(confirmerC).confirm(SUB_ID);
      expect(await contract.isComplete(SUB_ID)).to.equal(true);  // 3 of 3
    });
  });

  describe("confirmer governance", function () {
    it("only owner can add confirmers", async function () {
      await expect(contract.connect(outsider).addConfirmer(outsider.address))
        .to.be.revertedWith("CDF: not owner");
    });

    it("removed confirmer cannot confirm", async function () {
      await contract.connect(monitor).recordSubmission(SUB_ID, CID, 2);
      await contract.removeConfirmer(confirmerA.address);
      await expect(contract.connect(confirmerA).confirm(SUB_ID))
        .to.be.revertedWith("CDF: not authorized confirmer");
    });
  });
});
